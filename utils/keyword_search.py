def keyword_search(query, chunks, k=2):
    scores=[]
    query=query.lower()
    for chunk in chunks:
        chunk_lower=chunk.lower()
        score=0
        words=query.split()
        for word in words:
            if word in chunk_lower:
                score+=1
        scores.append((score, chunk))
    scores.sort(reverse=True)
    top_chunks=[]
    for score, chunk in scores[:k]:
        if score>0:
            top_chunks.append(chunk)
    return top_chunks