from sklearn.cluster import KMeans
import numpy as np

#groups semantically similar text chunks into clusters using KMeans on embedding vectors
def cluster_chunks(embeddings, n_clusters=4):
    embeddings = np.array(embeddings).astype(np.float32) #equired by ML libraries
    kmeans=KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels=kmeans.fit_predict(embeddings)
    return labels.tolist(), kmeans