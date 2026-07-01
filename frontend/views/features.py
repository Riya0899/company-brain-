# frontend/views/features.py
import streamlit as st

def render():
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-hero">
      <div class="cb-hero-badge">⚡ RAG · HDBSCAN · Hybrid Search · LLM-as-Judge</div>
      <h1>How <span>Company Brain</span> works</h1>
      <p>A full Retrieval-Augmented Generation pipeline — from raw PDF to intelligent, self-evaluated answers.</p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("🔢", "Semantic Vector Search", "Chunks embedded with all-MiniLM-L6-v2 (384-dim) and stored in ChromaDB."),
        ("🏔️", "HDBSCAN Topic Clustering", "Auto-discovers topic count from density — no fixed k needed. Noise chunks marked Miscellaneous."),
        ("🔍", "Hybrid Retrieval", "Semantic search + BM25 keyword search, both scoped to the predicted topic cluster."),
        ("💬", "Conversation Memory", "Last 4 messages fed into every prompt for natural follow-up questions."),
        ("⚖️", "LLM-as-Judge Scoring", "A second Groq model scores faithfulness + relevancy; low scores trigger a retry with a stronger prompt."),
        ("💡", "Smart Suggestions", "Groq generates starter questions after indexing, and 3 follow-ups after every answer."),
        ("⚠️", "Knowledge Gap Detection", "Any answer scoring below 50% confidence is logged as a gap for review."),
        ("📚", "Source Citations", "The LLM self-reports which sources it actually used via a SOURCES_USED tag."),
    ]

    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="cb-doc" style="align-items:flex-start;margin-bottom:10px">
              <div class="cb-doc-icon" style="font-size:18px">{icon}</div>
              <div>
                <div class="cb-doc-name">{title}</div>
                <div class="cb-doc-meta" style="line-height:1.5">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)