import chromadb

client = chromadb.PersistentClient(path = "vector_store")  # connection to database 

collection = client.get_or_create_collection(name = "company_documents") #collection is similar to SQL table
def store_chunks(chunks, embeddings, pdf_name, labels, ids=None, sources=None):
    n = len(chunks)
    final_ids = ids if ids is not None else [f"{pdf_name}_{i}" for i in range(n)]
    final_sources = sources if sources is not None else [pdf_name] * n

    collection.upsert(
        ids=list(final_ids),
        documents=list(chunks),
        embeddings=[e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings],
        metadatas=[
            {"source": final_sources[i], "chunk": i, "cluster": int(labels[i])}
            for i in range(n)
        ],
    )

def search_chunks(query_embedding, k=3):
    results=collection.query(
    query_embeddings = [query_embedding[0].tolist()],
    n_results=k,
    include=["documents", "metadatas"]
    )
    
    return results

def get_all_chunks():
    results=collection.get() #return everything
    return results["documents"] #returns only text

def get_cluster_chunks(cluster_id):

    results = collection.get(where={"cluster": int(cluster_id)})
    return results["documents"]



def search_cluster_chunks(
    query_embedding,
    cluster_id,
    k=3
):
    
    results=collection.query(
        query_embeddings=[
            query_embedding[0].tolist()
        ],
        n_results=k,
        where={
            "cluster":int(cluster_id)
        },
        include=[
            "documents",
            "metadatas"
        ]
    )
    return results