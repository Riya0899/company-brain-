COMPANY BRAIN — RAG PIPELINE OVERVIEW

═══════════════════════════════════════════════════════════════
1. DOCUMENT UPLOAD  (POST /upload or /upload-url)
═══════════════════════════════════════════════════════════════
File: main.py -> _index_text()

  a) Extract raw text
     - PDF:  utils/pdf_reader.py     -> extract_text_from_pdf()
     - URL:  utils/url_reader.py     -> extract_text_from_url()

  b) Split into overlapping chunks (1000 chars, 200 overlap)
     - utils/text_splitter.py        -> spit_text_into_chunks()

  c) Embed each chunk into a 384-dim vector
     - utils/embeddings.py           -> create_embeddings()
     - Model: sentence-transformers 'all-MiniLM-L6-v2'

  d) Cluster ALL chunks (old + new) by topic using HDBSCAN
     - utils/topic_clustering.py     -> cluster_chunks()
     - Re-clusters everything on every upload to keep cluster IDs consistent

  e) Name each cluster using Groq (one batched call, avoids duplicate names)
     - utils/topic_namer.py          -> generate_all_topic_names()

  f) Persist chunks + embeddings + metadata to ChromaDB
     - utils/vector_store.py         -> store_chunks()

  g) Generate starter questions + a document summary (Groq)
     - utils/suggestion_generator.py -> generate_suggestions()
     - utils/summarizer.py           -> summarize_document()

  h) Save document metadata to SQLite
     - db.py                         -> add_document()

  i) Invalidate the answer cache (new content may change old answers)
     - state.py                      -> kb.answer_cache = {}


═══════════════════════════════════════════════════════════════
2. ASKING A QUESTION  (POST /chat)
═══════════════════════════════════════════════════════════════
File: main.py -> chat()

  a) Check cache for an identical prior question -> instant return if hit

  b) Build recent chat history (last 4 messages)
     - utils/chat_memory.py          -> get_recent_chat()

  c) Retrieve relevant chunks (hybrid: semantic + keyword)
     - utils/hybrid_search.py        -> hybrid_retrieve()
       - Predicts which topic cluster the question belongs to
         (utils/topic_clustering.py -> predict_cluster())
       - Semantic search within that cluster (ChromaDB)
       - BM25 keyword search within that cluster
       - Merges + deduplicates both result sets

  d) Generate an answer, with judge-and-retry
     - utils/llm.py                  -> generate_answer_with_retry()
       - Calls Groq (llama-3.3-70b) with system prompt + context + question
       - Judges the answer's faithfulness + relevancy
         (utils/evaluator.py -> evaluate_answer(), using DeepEval + a second
          Groq model as judge)
       - Retries (up to 2x) with a stronger prompt if the judge scores low

  e) Extract which sources the model actually cited
     - main.py                       -> extract_sources_used()

  f) Log the question + scores to SQLite (for dashboard stats + gap detection)
     - db.py                         -> add_query(), add_gap()

  g) Cache the response, return it to the frontend


═══════════════════════════════════════════════════════════════
3. FOLLOW-UP SUGGESTIONS  (POST /followups, called AFTER the answer
   is already shown to the user, so it doesn't block their response)
═══════════════════════════════════════════════════════════════
  - utils/suggestion_generator.py    -> generate_followup_suggestions()


═══════════════════════════════════════════════════════════════
4. BACKEND STARTUP
═══════════════════════════════════════════════════════════════
File: main.py -> startup_event()

  - Reloads all chunks/embeddings from ChromaDB (which persists across
    restarts) back into the in-memory `kb` object (which does NOT persist)
  - Re-fits HDBSCAN on the reloaded embeddings, since the fitted clusterer
    object itself was never saved anywhere — only its output labels were
