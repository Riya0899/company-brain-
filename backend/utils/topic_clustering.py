import hdbscan
import numpy as np


def cluster_chunks(embeddings, min_cluster_size=2, min_samples=1):
    
    embeddings = np.array(embeddings).astype(np.float64)  # hdbscan prefers float64

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_epsilon=0.0, #controls whether nearby clusters should be merged
        prediction_data=True,  # Required to enable approximate_predict() later
    )
    labels = clusterer.fit_predict(embeddings)

    return labels.tolist(), clusterer


def get_dynamic_min_cluster_size(num_chunks, base= 2, scale_every = 500, max_size = 40):
    
    # Scales min_cluster_size with knowledge base size, so clusters stay
    # meaningfully sized as you go from hundreds to tens of thousands of chunks.

    size = base + (num_chunks // scale_every)
    return max(base, min(max_size, size))

def predict_cluster(clusterer, query_embedding):
   
    query_embedding = np.array(query_embedding).astype(np.float64).reshape(1, -1)
    labels, strengths = hdbscan.approximate_predict(clusterer, query_embedding)
    return int(labels[0])