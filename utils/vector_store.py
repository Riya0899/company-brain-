import chromadb

client = chromadb.PersistentClient(path = "vector_store")  # connection to database 

collection = client.get_or_create_collection(name = "company_documents") #collection is similar to SQL table
def store_chunks(chunks, embeddings,pdf_name, labels):
    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{pdf_name}_{i}"],
            documents=[chunk],
            embeddings=[embeddings[i].tolist()],
            metadatas=[{
                "source":pdf_name,
                "chunk":i,
                "cluster":int(labels[i])
            }]
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