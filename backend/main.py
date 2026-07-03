# backend/main.py
import re
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
from state import kb
from utils.vector_store import collection
from utils.pdf_reader import extract_text_from_pdf
from utils.url_reader import extract_text_from_url
from utils.text_splitter import split_text_into_chunks
from utils.embeddings import create_embeddings, model as embed_model
from utils.topic_clustering import cluster_chunks, get_dynamic_min_cluster_size
from utils.topic_namer import generate_all_topic_names
from utils.hybrid_search import hybrid_retrieve
from utils.vector_store import store_chunks
from utils.llm import generate_answer_with_retry
from utils.summarizer import summarize_document
from utils.suggestion_generator import generate_suggestions, generate_followup_suggestions
from utils.chat_memory import get_recent_chat

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
db.init_db()


def _rebuild_state_from_chroma():
    """On backend startup, reload all persisted chunks from ChromaDB back into kb,
    so a restart doesn't lose the in-memory clustering state."""
    all_data = collection.get(include=["documents", "embeddings", "metadatas"])
    if not all_data["ids"]:
        return  # nothing indexed yet, nothing to rebuild

    kb.all_chunks = all_data["documents"]
    kb.all_embeddings = list(all_data["embeddings"])
    kb.all_sources = [m["source"] for m in all_data["metadatas"]]
    kb.all_chunk_ids = all_data["ids"]

    all_emb = np.array(kb.all_embeddings).astype(np.float32)
    min_size = get_dynamic_min_cluster_size(len(all_emb))
    labels, clusterer = cluster_chunks(all_emb, min_cluster_size=min_size, min_samples=1)
    kb.cluster_labels = labels
    kb.clusterer = clusterer

    kb.topic_names = db.list_topics()
    # convert string keys back to int if needed (SQLite may return them fine already)
    kb.topic_names = {int(k): v for k, v in kb.topic_names.items()}


@app.on_event("startup")
def startup_event():
    _rebuild_state_from_chroma()
def _remove_existing_document(source_name: str):
    """Purge any previously indexed data for this source_name from kb, Chroma, and SQLite,
    so re-uploading a file with the same name cleanly replaces it instead of erroring/duplicating."""
    if source_name not in kb.all_sources:
        return  # nothing to remove, first-time upload

    keep_idx = [i for i, s in enumerate(kb.all_sources) if s != source_name]

    kb.all_chunks = [kb.all_chunks[i] for i in keep_idx]
    kb.all_embeddings = [kb.all_embeddings[i] for i in keep_idx]
    kb.all_sources = [kb.all_sources[i] for i in keep_idx]
    kb.all_chunk_ids = [kb.all_chunk_ids[i] for i in keep_idx]

    # remove old vectors from Chroma
    collection.delete(where={"source": source_name})

    kb.doc_chunk_counts.pop(source_name, None)
    kb.doc_summaries.pop(source_name, None)
    kb.answer_cache = {}  # context changed, cache is now stale

class ChatRequest(BaseModel):
    query: str
    messages: list[dict] = []   # [{"role": "user"/"assistant", "content": "..."}]


class UrlRequest(BaseModel):
    url: str
    max_depth: int = 2
    max_pages: int = 10


def extract_sources_used(answer: str):
    match = re.search(r"SOURCES_USED:\s*(.+)$", answer, re.MULTILINE)
    if match:
        clean = answer[:match.start()].strip()
        used = [s.strip() for s in match.group(1).split(",") if s.strip()]
        return clean, used
    return answer, []


def _index_text(text: str, source_name: str):
    _remove_existing_document(source_name)
    chunks = split_text_into_chunks(text)
    embeddings = create_embeddings(chunks)

    for i, chunk in enumerate(chunks):
        kb.all_chunks.append(chunk)
        kb.all_embeddings.append(embeddings[i])
        kb.all_sources.append(source_name)
        kb.all_chunk_ids.append(f"{source_name}_{i}")
        
    kb.answer_cache = {} 
    
    all_emb = np.array(kb.all_embeddings).astype(np.float32)
    min_size = get_dynamic_min_cluster_size(len(all_emb))
    labels, clusterer = cluster_chunks(all_emb, min_cluster_size=min_size, min_samples=1)
    kb.cluster_labels = labels
    kb.clusterer = clusterer

    cluster_samples = {}
    for cid in set(labels):
        if cid == -1:
            continue
        cluster_samples[cid] = [kb.all_chunks[i] for i in range(len(labels)) if labels[i] == cid]

    topic_names = generate_all_topic_names(cluster_samples) if cluster_samples else {}
    if -1 in set(labels):
        topic_names[-1] = "Miscellaneous"
    kb.topic_names = topic_names
    db.save_topics(topic_names)

    store_chunks(kb.all_chunks, np.array(kb.all_embeddings), "global", labels,
                 ids=kb.all_chunk_ids, sources=kb.all_sources)

    kb.doc_chunk_counts[source_name] = len(chunks)

    label = f"PDF ({source_name})"
    new_suggestions = generate_suggestions(chunks, n=8, source_label=label)
    for s in new_suggestions:
        if s not in kb.pdf_suggestions:
            kb.pdf_suggestions.append(s)
    kb.pdf_suggestions = kb.pdf_suggestions[-20:]

    summary = summarize_document(chunks, source_label=label)
    kb.doc_summaries[source_name] = summary
    db.add_document(source_name, len(chunks), summary)

    return chunks, topic_names, summary

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file.file)
    chunks, topic_names, summary = _index_text(text, file.filename)
    return {"filename": file.filename, "chunks": len(chunks), "topics": topic_names, "summary": summary}


@app.post("/upload-url")
def upload_url(req: UrlRequest):
    try:
        text, source_name = extract_text_from_url(req.url, max_depth=req.max_depth, max_pages=req.max_pages)
    except ValueError as e:
        raise HTTPException(400, str(e))
    chunks, topic_names, summary = _index_text(text, source_name)
    return {"filename": source_name, "chunks": len(chunks), "topics": topic_names, "summary": summary}


@app.post("/chat")
def chat(req: ChatRequest):
    if not kb.all_chunks or kb.clusterer is None:
        raise HTTPException(400, "No documents indexed yet.")

    cache_key = req.query.strip().lower()
    if cache_key in kb.answer_cache:
        return kb.answer_cache[cache_key]   # instant return, no pipeline run at all

    chat_history = get_recent_chat(req.messages)
    retrieval = hybrid_retrieve(
        user_query=req.query,
        embed_model=embed_model,
        clusterer=kb.clusterer,
        topic_names=kb.topic_names,
        vector_k=3,
        keyword_k=2,
    )
    context, sources, topic_name = retrieval["context"], retrieval["sources"], retrieval["topic_name"]

    final_context = f"conversation history:\n{chat_history}\n\nknowledge base:\n{context}"
    answer, score, attempts, reason, faith, rel = generate_answer_with_retry(final_context, req.query, max_retries=2)
    clean_answer, used_names = extract_sources_used(answer)

    used_sources = sources
    if used_names:
        used_lower = [u.lower() for u in used_names]
        filtered = [s for s in sources if any(u in s["source"].lower() or s["source"].lower() in u for u in used_lower)]
        if filtered:
            used_sources = filtered

    db.add_query(req.query, score, faith, rel, topic_name)
    if score < 0.5:
        db.add_gap(req.query)

    response = {
        "answer": clean_answer,
        "score": round(score, 2),
        "faithfulness": round(faith, 2),
        "relevancy": round(rel, 2),
        "topic": topic_name,
        "sources": used_sources,
    }

    kb.answer_cache[cache_key] = response   # NEW: save for next time
    return response


@app.get("/documents")
def get_documents():
    return db.list_documents()


@app.get("/topics")
def get_topics():
    return db.list_topics()


@app.get("/gaps")
def get_gaps():
    return db.list_gaps()


@app.get("/history")
def get_history():
    return db.list_queries()


@app.get("/suggestions")
def get_suggestions():
    return kb.pdf_suggestions

@app.get("/stats")
def get_stats():
    history = db.list_queries()
    if not history:
        return {"avg_score": 0, "avg_faithfulness": 0, "avg_relevancy": 0, "total_queries": 0}
    n = len(history)
    return {
        "avg_score": sum(h["score"] for h in history) / n,
        "avg_faithfulness": sum(h["faithfulness"] or 0 for h in history) / n,
        "avg_relevancy": sum(h["relevancy"] or 0 for h in history) / n,
        "total_queries": n,
    }