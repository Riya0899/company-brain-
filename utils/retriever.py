from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_top_k_chunks(query, chunks, chunk_embeddings, k=3):
    query_embedding = model.encode([query])
    scores = cosine_similarity(query_embedding, chunk_embeddings)[0]
    top_k_indices = np.argsort(scores)[-k:][::-1] #sort an array
    top_chunks = [chunks[i] for i in top_k_indices]
    return top_chunks