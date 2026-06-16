from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
#thise model already learned - language meaning, similarity, context relation

def create_embeddings(chunks):
    embeddings = model.encode(chunks)
    return embeddings.astype('float64')


