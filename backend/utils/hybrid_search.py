from rank_bm25 import BM25Okapi    # rank based bm25 technique
import re                        # regex for cleaning
import numpy as np
import nltk   # nltk-natural language toolkit 
from nltk.corpus import stopwords
from utils.topic_clustering import predict_cluster
from utils.vector_store import search_cluster_chunks, get_cluster_chunks,search_chunks, get_all_chunks

try:
    nltk.data.find("corpora/stopwords")  # checks whether the download has already happened
except LookupError:
    nltk.download("stopwords")

STOPWORDS = set(stopwords.words("english"))

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    words=re.findall(r"\b[a-z0-9]+\b", text)
    return [w for w in words if w not in STOPWORDS]


def _bm25_search(query: str, chunk_meta_pairs: list[tuple], k: int = 2) -> list[tuple]:
    if not chunk_meta_pairs:
        return []
    chunks = [c for c, m in chunk_meta_pairs]
    tokenized_corpus = [_tokenize(c) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(query))
    scored = sorted(zip(scores, chunk_meta_pairs), key=lambda x: x[0], reverse=True)
    return [pair for score, pair in scored[:k] if score > 0]

def predict_topic_cluster(clusterer, query_embedding):
    return predict_cluster(clusterer, query_embedding)


def hybrid_retrieve(
    user_query: str,
    embed_model,
    clusterer,
    topic_names: dict,
    vector_k: int = 3,
    keyword_k: int = 2,
) -> dict:
    query_embedding = embed_model.encode(user_query, convert_to_numpy=True)
    query_embedding = query_embedding.astype(np.float32).reshape(1, -1)

    topic_id = predict_topic_cluster(clusterer, query_embedding)
    topic_name = topic_names.get(topic_id, f"Cluster {topic_id}")

    if topic_id == -1:
        vector_results = search_chunks(query_embedding, k=vector_k)
        vector_chunks = vector_results["documents"][0]
        vector_metadatas = vector_results["metadatas"][0]
        cluster_chunks_only = get_all_chunks()          # now list of (text, meta)
    else:
        vector_results = search_cluster_chunks(query_embedding, topic_id, k=vector_k)
        vector_chunks = vector_results["documents"][0]
        vector_metadatas = vector_results["metadatas"][0]
        cluster_chunks_only = get_cluster_chunks(topic_id)  # now list of (text, meta)

    keyword_pairs = _bm25_search(user_query, cluster_chunks_only, k=keyword_k)

    # combine vector + keyword as (text, meta) pairs, deduped by text
    combined = list(zip(vector_chunks, vector_metadatas))
    existing_texts = {c for c, m in combined}
    for c, m in keyword_pairs:
        if c not in existing_texts:
            combined.append((c, m))
            existing_texts.add(c)

    context = ""
    sources = []
    for idx, (chunk, meta) in enumerate(combined):
        meta = meta or {}
        source = meta.get("source", "unknown")
        cluster_id = meta.get("cluster")
        cluster_label = topic_names.get(cluster_id, f"Cluster {cluster_id}") if cluster_id is not None else topic_name

        best_line = _find_best_line(user_query, chunk)   # NEW

        context += f"""
Document {idx+1}
Source: {source}

{chunk}

--------------------
"""
        sources.append({
            "doc_no": idx + 1,
            "source": source,
            "cluster": cluster_label,
            "chunk_index": meta.get("chunk"),
            "matched_line": best_line,      # NEW — the actual sentence, not a snippet
            "snippet": chunk[:180] + ("…" if len(chunk) > 180 else "")
        })
    return {"context": context, "sources": sources, "topic_name": topic_name, "topic_id": topic_id}   
        
        
def _find_best_line(query: str, chunk_text: str) -> str:
    """Given a chunk, find the single sentence/line most relevant to the query."""
    lines = [l.strip() for l in re.split(r'(?<=[.?!])\s+|\n', chunk_text) if l.strip()]
    if not lines:
        return chunk_text[:180]
    if len(lines) == 1:
        return lines[0]

    tokenized_lines = [_tokenize(l) for l in lines]
    bm25 = BM25Okapi(tokenized_lines)
    scores = bm25.get_scores(_tokenize(query))
    best_idx = int(np.argmax(scores))
    return lines[best_idx]