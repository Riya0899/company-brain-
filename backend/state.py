# backend/state.py

class KnowledgeBase:
    def __init__(self):
        self.all_chunks = []
        self.all_embeddings = []
        self.all_sources = []
        self.all_chunk_ids = []
        self.clusterer = None
        self.cluster_labels = []
        self.topic_names = {}
        self.doc_chunk_counts = {}
        self.pdf_suggestions = []
        self.doc_summaries = {}
        self.answer_cache = {}

kb = KnowledgeBase()