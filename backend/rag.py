# backend/rag.py
import os
import re
import numpy as np
import hdbscan
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from groq import Groq
from pypdf import PdfReader

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client = Groq(api_key=os.environ["GROQ_API_KEY"])


def extract_pdf_text(file) -> str:
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, size=1000, overlap=200) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def embed_chunks(chunks: list[str]) -> np.ndarray:
    return embed_model.encode(chunks)


def recluster(kb):
    """HDBSCAN auto-discovers cluster count from density. -1 = noise/misc."""
    matrix = np.array(kb.embeddings)
    min_size = max(2, len(matrix) // 10)
    model = hdbscan.HDBSCAN(min_cluster_size=min_size, min_samples=1)
    labels = model.fit_predict(matrix)
    kb.clusterer = model
    kb.cluster_labels = list(labels)


def rebuild_bm25(kb):
    """Rebuild BM25 index on all chunks. Call after every upload."""
    tokenized = [tokenize(c) for c in kb.chunks]
    kb.bm25 = BM25Okapi(tokenized)


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def name_topics(kb) -> dict:
    samples = {}
    for cid in set(kb.cluster_labels):
        if cid == -1:
            continue
        idxs = [i for i, l in enumerate(kb.cluster_labels) if l == cid][:3]
        samples[cid] = " / ".join(kb.chunks[i][:150] for i in idxs)

    if not samples:
        return {-1: "Miscellaneous"}

    prompt = "Give each topic a short 2-4 word name. Respond as 'id: name' per line.\n\n"
    for cid, text in samples.items():
        prompt += f"Cluster {cid}: {text}\n"

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    names = {}
    for line in resp.choices[0].message.content.splitlines():
        if ":" in line:
            cid_str, name = line.split(":", 1)
            try:
                names[int(cid_str.strip().split()[-1])] = name.strip()
            except ValueError:
                continue
    if -1 in set(kb.cluster_labels):
        names[-1] = "Miscellaneous"
    return names


def summarize(text: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Summarize in 4 sentences:\n\n{text[:4000]}"}],
    )
    return resp.choices[0].message.content


def semantic_search(kb, query: str, k=5) -> list[int]:
    q_vec = embed_model.encode([query])[0]
    matrix = np.array(kb.embeddings)
    sims = matrix @ q_vec / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(q_vec) + 1e-8)
    return list(np.argsort(sims)[::-1][:k])


def bm25_search(kb, query: str, k=5) -> list[int]:
    scores = kb.bm25.get_scores(tokenize(query))
    return list(np.argsort(scores)[::-1][:k])


def hybrid_retrieve(kb, query: str, vector_k=3, keyword_k=2) -> list[dict]:
    """Combine semantic + BM25 results, de-duplicated."""
    if not kb.chunks:
        return []
    sem_idx = semantic_search(kb, query, vector_k)
    kw_idx = bm25_search(kb, query, keyword_k)
    combined = list(dict.fromkeys(sem_idx + kw_idx))  # dedupe, keep order

    q_vec = embed_model.encode([query])[0]
    matrix = np.array(kb.embeddings)
    sims = matrix @ q_vec / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(q_vec) + 1e-8)

    return [
        {"chunk": kb.chunks[i], "source": kb.sources[i], "score": float(sims[i])}
        for i in combined
    ]


def generate_answer(query: str, retrieved: list[dict]) -> dict:
    context = "\n\n".join(r["chunk"] for r in retrieved)
    prompt = f"""Answer using only this context. If it's not enough, say so.

Context:
{context}

Question: {query}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Answer only from the given context."},
                  {"role": "user", "content": prompt}],
    )
    answer = resp.choices[0].message.content
    confidence = min(r["score"] for r in retrieved) if retrieved else 0.0
    return {"answer": answer, "score": round(float(confidence), 2)}