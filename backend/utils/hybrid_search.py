# hybrid search.py

from rank_bm25 import BM25Okapi
import re
import numpy as np
from utils.topic_clustering import predict_cluster
from utils.vector_store import search_cluster_chunks, get_cluster_chunks,search_chunks, get_all_chunks


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"\b[a-z0-9]+\b", text)


def _bm25_search(query: str, chunks: list[str], k: int = 2) -> list[str]:
    if not chunks:
        return []
    tokenized_corpus = [_tokenize(c) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(query))
    scored = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [c for score, c in scored[:k] if score > 0]


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
        # No confident cluster match — fall back to searching across
        # ALL chunks globally for both methods, rather than returning nothing.
        
        vector_results = search_chunks(query_embedding, k=vector_k)
        vector_chunks = vector_results["documents"][0]
        vector_metadatas = vector_results["metadatas"][0]
        cluster_chunks_only = get_all_chunks()
    else:
        vector_results = search_cluster_chunks(query_embedding, topic_id, k=vector_k)
        vector_chunks = vector_results["documents"][0]
        vector_metadatas = vector_results["metadatas"][0]
        cluster_chunks_only = get_cluster_chunks(topic_id)

    keyword_chunks = _bm25_search(user_query, cluster_chunks_only, k=keyword_k)

    combined_chunks = list(vector_chunks)
    for c in keyword_chunks:
        if c not in combined_chunks:
            combined_chunks.append(c)

    context = ""
    sources = []
    for idx, chunk in enumerate(combined_chunks):
        source = "keyword search"
        if idx < len(vector_metadatas) and vector_metadatas[idx]:
            source = vector_metadatas[idx].get("source", "unknown")
        context += f"{chunk} (Source: {source})\n\n"
        sources.append({"source": source, "snippet": chunk[:180] + ("…" if len(chunk) > 180 else "")})

    return {"context": context, "sources": sources, "topic_name": topic_name, "topic_id": topic_id}