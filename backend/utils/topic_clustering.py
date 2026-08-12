import hdbscan
import numpy as np

def cluster_chunks(embeddings, min_cluster_size=2, min_samples=1):
    
    embeddings = np.array(embeddings).astype(np.float64)  # hdbscan prefers float64

    n_samples = embeddings.shape[0]
    if n_samples <= min_samples:
        # Not enough chunks yet to cluster meaningfully — treat everything as
        # unclustered/noise instead of letting HDBSCAN crash on too few points.
        return [-1] * n_samples, None

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        
        cluster_selection_epsilon=0.0,
        prediction_data=True,  # Required to enable approximate_predict() later
    )
    labels = clusterer.fit_predict(embeddings)

    return labels.tolist(), clusterer


def get_dynamic_min_cluster_size(num_chunks: int, base: int = 5, scale_every: int = 500, max_size: int = 40) -> int:
    
    # Scales min_cluster_size with knowledge base size, so clusters stay
    # meaningfully sized as you go from hundreds to tens of thousands of chunks.

    size = base + (num_chunks // scale_every)
    return max(base, min(max_size, size))

def predict_cluster(clusterer, query_embedding):
    if clusterer is None:
        return -1

    query_embedding = np.array(query_embedding).astype(np.float64).reshape(1, -1)
    labels, strengths = hdbscan.approximate_predict(clusterer, query_embedding)
    return int(labels[0])