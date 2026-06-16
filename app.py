import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Company Brain", layout="wide", page_icon="🧠")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 0 !important; max-width: 100% !important;}
section[data-testid="stSidebar"] {display: none;}

body, .stApp { background: #0e0e11 !important; color: #ccc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

/* ── Top nav bar ── */
.cb-topbar {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 28px; background: #13131a;
    border-bottom: 0.5px solid #232330; position: sticky; top: 0; z-index: 100;
}
.cb-logo { display: flex; align-items: center; gap: 10px; margin-right: 20px; }
.cb-logo-icon {
    width: 34px; height: 34px; background: linear-gradient(135deg,#6B5CE7,#a78bfa);
    border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 17px;
    box-shadow: 0 0 16px #6B5CE733;
}
.cb-logo-text { color: #fff; font-size: 15px; font-weight: 600; letter-spacing: -0.3px; }
.cb-logo-sub { font-size: 10px; color: #555; font-weight: 400; letter-spacing: 0; }
.cb-search {
    flex: 1; max-width: 480px; display: flex; align-items: center; gap: 8px;
    background: #1a1a24; border: 0.5px solid #2e2e42; border-radius: 8px; padding: 8px 14px;
    transition: border-color .2s;
}
.cb-search:focus-within { border-color: #6B5CE7; }
.cb-search input { background: none; border: none; outline: none; color: #ccc; font-size: 13px; width: 100%; }
.cb-search-icon { color: #444; font-size: 13px; }
.cb-nav-pills { display: flex; gap: 4px; margin-left: auto; }
.cb-nav-pill {
    padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500;
    color: #666; background: none; border: 0.5px solid transparent; cursor: pointer; transition: all .15s;
}
.cb-nav-pill:hover { color: #aaa; border-color: #2e2e42; }
.cb-nav-pill-active { color: #a78bfa !important; background: #1e1a35 !important; border-color: #6B5CE744 !important; }
.cb-btn-upload {
    padding: 7px 16px; border-radius: 7px; border: none;
    background: linear-gradient(135deg,#6B5CE7,#8b5cf6); color: #fff;
    font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
    box-shadow: 0 2px 12px #6B5CE744;
}

/* ── Content ── */
.cb-content { padding: 24px 28px; }

/* ── Hero banner ── */
.cb-hero {
    background: linear-gradient(135deg, #13131a 0%, #1a1630 50%, #13131a 100%);
    border: 0.5px solid #2e2e42; border-radius: 14px;
    padding: 36px 40px; margin-bottom: 24px; position: relative; overflow: hidden;
}
.cb-hero::before {
    content: ''; position: absolute; top: -60px; right: -40px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, #6B5CE722 0%, transparent 70%); pointer-events: none;
}
.cb-hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1e1a35; border: 0.5px solid #6B5CE744; border-radius: 20px;
    padding: 4px 12px; font-size: 11px; color: #a78bfa; margin-bottom: 14px;
}
.cb-hero-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #6B5CE7; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.cb-hero h1 {
    font-size: 30px; font-weight: 700; color: #fff;
    margin: 0 0 10px; letter-spacing: -0.8px; line-height: 1.2;
}
.cb-hero h1 span { background: linear-gradient(90deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.cb-hero p { font-size: 14px; color: #777; line-height: 1.7; max-width: 560px; margin: 0 0 22px; }
.cb-hero-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.cb-hero-btn {
    padding: 10px 22px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
    display: inline-flex; align-items: center; gap: 7px; transition: all .15s;
}
.cb-hero-btn-primary {
    background: linear-gradient(135deg,#6B5CE7,#8b5cf6); border: none; color: #fff;
    box-shadow: 0 2px 16px #6B5CE744;
}
.cb-hero-btn-primary:hover { box-shadow: 0 4px 24px #6B5CE766; transform: translateY(-1px); }
.cb-hero-btn-secondary {
    background: #1a1a24; border: 0.5px solid #2e2e42; color: #aaa;
}
.cb-hero-btn-secondary:hover { border-color: #444; color: #ccc; }

/* ── Stat cards ── */
.cb-stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px; }
.cb-stat {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px; padding: 18px 20px;
    transition: border-color .2s;
}
.cb-stat:hover { border-color: #3a3a50; }
.cb-stat-num { font-size: 32px; font-weight: 700; margin-bottom: 4px; letter-spacing: -1px; }
.cb-stat-label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
.cb-stat-change { font-size: 10px; color: #4CAF7D; margin-top: 6px; }

/* ── Features grid ── */
.cb-features { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 24px; }
.cb-feature {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px; padding: 20px;
    transition: all .2s;
}
.cb-feature:hover { border-color: #3a3a50; background: #16161f; transform: translateY(-2px); }
.cb-feature-icon {
    width: 40px; height: 40px; border-radius: 10px; margin-bottom: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.cb-feature h3 { font-size: 13px; color: #ddd; font-weight: 600; margin: 0 0 6px; }
.cb-feature p { font-size: 12px; color: #555; line-height: 1.6; margin: 0; }

/* ── How it works ── */
.cb-steps { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px; }
.cb-step {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px; padding: 18px;
    position: relative;
}
.cb-step-num {
    font-size: 11px; font-weight: 700; color: #6B5CE7; background: #1e1a35;
    border: 0.5px solid #6B5CE744; border-radius: 6px; padding: 2px 8px;
    display: inline-block; margin-bottom: 12px; letter-spacing: 0.5px;
}
.cb-step h4 { font-size: 12px; font-weight: 600; color: #ccc; margin: 0 0 6px; }
.cb-step p { font-size: 11px; color: #555; line-height: 1.6; margin: 0; }
.cb-step-arrow {
    position: absolute; right: -20px; top: 50%; transform: translateY(-50%);
    color: #333; font-size: 14px; z-index: 1;
}

/* ── Document cards ── */
.cb-docs { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 20px; }
.cb-doc {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px;
    padding: 16px; cursor: pointer; transition: all .15s;
}
.cb-doc:hover { border-color: #3a3a50; background: #16161f; }
.cb-doc-icon { width: 38px; height: 38px; border-radius: 9px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.cb-doc-name { font-size: 13px; color: #ccc; font-weight: 500; margin-bottom: 6px; }
.cb-doc-meta { font-size: 11px; color: #555; display: flex; align-items: center; gap: 6px; }
.cb-tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 500; }
.tag-ai  { background: #2a2560; color: #9B8FF5; }
.tag-doc { background: #0d1e35; color: #5BA4E5; }

/* ── Query history ── */
.cb-query-item {
    background: #13131a; border: 0.5px solid #232330; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 12px;
    transition: border-color .15s;
}
.cb-query-item:hover { border-color: #3a3a50; }
.cb-query-q { font-size: 12px; color: #bbb; font-weight: 500; margin-bottom: 3px; }
.cb-query-meta { font-size: 10px; color: #444; }
.cb-query-score {
    font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 6px; white-space: nowrap; margin-left: auto;
}
.score-high { background: #0d2e1a; color: #4CAF7D; }
.score-mid  { background: #2e2010; color: #E5945B; }
.score-low  { background: #2e1010; color: #E57070; }

/* ── Gap / knowledge gap ── */
.cb-gap {
    background: #1a150d; border: 0.5px solid #3a2e10; border-radius: 12px;
    padding: 14px 18px; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 20px;
}
.cb-gap-icon { width: 30px; height: 30px; background: #2a2210; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 14px; }
.cb-gap-text { font-size: 12px; color: #a08040; line-height: 1.6; }
.cb-gap-text strong { color: #d4a840; }

/* ── Knowledge gap list ── */
.cb-gap-item {
    background: #1a150d; border: 0.5px solid #3a2e10; border-radius: 9px;
    padding: 10px 14px; margin-bottom: 7px; display: flex; align-items: center; gap: 10px;
}
.cb-gap-q { font-size: 12px; color: #a08040; flex: 1; }

/* ── Chat ── */
.cb-topic-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1e1a35; border: 0.5px solid #3a3060; border-radius: 6px;
    padding: 5px 11px; font-size: 11px; color: #8B7FF0; margin-bottom: 6px;
}
.cb-quality {
    background: #161616; border: 0.5px solid #2a2a2a; border-radius: 8px;
    padding: 10px 12px; margin-top: 8px; font-size: 11px;
}

/* ── Upload ── */
.cb-file-item {
    background: #13131a; border: 0.5px solid #232330; border-radius: 11px;
    padding: 14px 18px; display: flex; align-items: center; gap: 12px; margin-bottom: 8px;
}
.cb-file-icon { width: 38px; height: 38px; background: #1e1020; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 17px; flex-shrink: 0; }
.cb-file-info { flex: 1; }
.cb-file-name { font-size: 13px; color: #ccc; font-weight: 500; margin-bottom: 3px; }
.cb-file-sub { font-size: 10px; color: #555; }
.cb-prog-bg { height: 3px; background: #2a2a2a; border-radius: 2px; margin-top: 6px; overflow: hidden; }
.cb-prog { height: 3px; border-radius: 2px; }
.cb-status { font-size: 10px; font-weight: 600; padding: 3px 10px; border-radius: 6px; white-space: nowrap; }
.status-indexed  { background: #0d2e1a; color: #4CAF7D; }
.status-indexing { background: #2a2560; color: #9B8FF5; }

/* ── Bubble chat ── */
.stChatMessage { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 12px !important; }
.stChatInput > div { background: #1a1a24 !important; border: 0.5px solid #2e2e42 !important; border-radius: 10px !important; }
.stChatInput textarea { color: #ccc !important; background: transparent !important; }
.stFileUploader { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 10px !important; }
div[data-testid="stFileUploadDropzone"] { background: #16161f !important; border: 1.5px dashed #2e2e42 !important; border-radius: 10px !important; }
.stProgress > div > div { background: linear-gradient(90deg, #6B5CE7, #a78bfa) !important; }
.stExpander { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 8px !important; }
.stAlert { border-radius: 8px !important; }

/* ── Section headers ── */
.cb-sec-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.cb-sec-title { font-size: 14px; color: #bbb; font-weight: 600; letter-spacing: -0.2px; }
.cb-sec-sub { font-size: 11px; color: #555; }
.cb-divider { border: none; border-top: 0.5px solid #1e1e2a; margin: 24px 0; }

/* ── Insight cards ── */
.cb-insight {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px;
}
.cb-insight-title { font-size: 12px; font-weight: 600; color: #aaa; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.cb-pill-row { display: flex; gap: 6px; flex-wrap: wrap; }
.cb-pill {
    font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 500;
    background: #1e1a35; border: 0.5px solid #6B5CE744; color: #a78bfa;
}
.cb-pill-green { background: #0d2e1a; border-color: #4CAF7D44; color: #4CAF7D; }
.cb-pill-orange { background: #2e1e0d; border-color: #E5945B44; color: #E5945B; }
.cb-pill-blue { background: #0d1e35; border-color: #5BA4E544; color: #5BA4E5; }

/* ── RAG Pipeline diagram ── */
.cb-pipeline-wrap {
    background: #13131a; border: 0.5px solid #232330; border-radius: 14px;
    padding: 28px 32px; margin-bottom: 24px;
}
.cb-pipeline {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
}
.cb-pipeline-step {
    text-align: center; flex: 1; min-width: 90px;
}
.cb-pipeline-icon { font-size: 28px; margin-bottom: 6px; }
.cb-pipeline-label { font-size: 12px; font-weight: 600; color: #ccc; margin-bottom: 3px; }
.cb-pipeline-sub { font-size: 10px; color: #555; }
.cb-pipeline-arrow { color: #333; font-size: 20px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "processed_files": set(), "document_names": set(),
    "cluster_labels": None, "topic_names": {}, "chunk_cluster_map": {},
    "kmeans": None, "page": "dashboard",
    "query_history": [],       # list of {q, score, topic, ts}
    "knowledge_gaps": [],      # questions that got low-confidence answers
    "total_chunks_stored": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Top nav bar ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="cb-topbar">
  <div class="cb-logo">
    <div class="cb-logo-icon">🧠</div>
    <div>
      <div class="cb-logo-text">Company Brain</div>
      <div class="cb-logo-sub">Knowledge Intelligence</div>
    </div>
  </div>
  <div class="cb-search">
    <span class="cb-search-icon">🔍</span>
    <input type="text" placeholder="Search documents, topics, queries..." />
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page tabs ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5, col_gap = st.columns([1.2, 1, 1.2, 1.2, 1.2, 4])
with col1:
    if st.button("📊 Dashboard", use_container_width=True,
                 type="primary" if st.session_state.page == "dashboard" else "secondary"):
        st.session_state.page = "dashboard"; st.rerun()
with col2:
    if st.button("✨ Ask AI", use_container_width=True,
                 type="primary" if st.session_state.page == "chat" else "secondary"):
        st.session_state.page = "chat"; st.rerun()
with col3:
    if st.button("📤 Upload", use_container_width=True,
                 type="primary" if st.session_state.page == "upload" else "secondary"):
        st.session_state.page = "upload"; st.rerun()
with col4:
    if st.button("🔍 Knowledge Gaps", use_container_width=True,
                 type="primary" if st.session_state.page == "gaps" else "secondary"):
        st.session_state.page = "gaps"; st.rerun()
with col5:
    if st.button("⚡ Features", use_container_width=True,
                 type="primary" if st.session_state.page == "features" else "secondary"):
        st.session_state.page = "features"; st.rerun()

st.markdown("<hr style='border:none;border-top:0.5px solid #1e1e2a;margin:0'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    # Hero
    doc_count = len(st.session_state.document_names)
    if doc_count == 0:
        st.markdown("""
        <div class="cb-hero">
          <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>RAG-powered · Semantic Search · Topic Clustering</div>
          <h1>Your documents.<br><span>Intelligent answers.</span></h1>
          <p>Company Brain turns your PDFs into a searchable knowledge base — powered by vector embeddings, topic clustering, and OpenRouter AI. Upload once, ask anything.</p>
        </div>
        """, unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("📤 Upload your first PDF →", type="primary", use_container_width=True):
                st.session_state.page = "upload"; st.rerun()
    else:
        st.markdown(f"""
        <div class="cb-hero">
          <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>Knowledge base active · {doc_count} document{"s" if doc_count != 1 else ""} indexed</div>
          <h1>Ask anything about<br><span>your company docs.</span></h1>
          <p>Your knowledge base is live. Ask questions, explore topics, and discover insights across all {doc_count} uploaded document{"s" if doc_count != 1 else ""}.</p>
        </div>
        """, unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("✨ Ask a question →", type="primary", use_container_width=True):
                st.session_state.page = "chat"; st.rerun()

    # Stats
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    avg_score = 0
    if st.session_state.query_history:
        avg_score = sum(q["score"] for q in st.session_state.query_history) / len(st.session_state.query_history)

    st.markdown(f"""
    <div class="cb-stats">
      <div class="cb-stat">
        <div class="cb-stat-num" style="color:#a78bfa">{doc_count}</div>
        <div class="cb-stat-label">Documents indexed</div>
        <div class="cb-stat-change">📄 PDFs in knowledge base</div>
      </div>
      <div class="cb-stat">
        <div class="cb-stat-num" style="color:#4CAF7D">{msg_count}</div>
        <div class="cb-stat-label">Queries answered</div>
        <div class="cb-stat-change">🔍 Total AI responses</div>
      </div>
      <div class="cb-stat">
        <div class="cb-stat-num" style="color:#E5945B">{len(st.session_state.topic_names)}</div>
        <div class="cb-stat-label">Topics discovered</div>
        <div class="cb-stat-change">🏷️ Auto-clustered by AI</div>
      </div>
      <div class="cb-stat">
        <div class="cb-stat-num" style="color:#60a5fa">{int(avg_score * 100)}%</div>
        <div class="cb-stat-label">Avg. confidence</div>
        <div class="cb-stat-change">📊 Across all answers</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout: left = charts / topics, right = query history
    left, right = st.columns([3, 2], gap="medium")

    with left:
        # Topic cluster chart
        if st.session_state.cluster_labels is not None:
            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🏷️ Topic clusters</span><span class="cb-sec-sub">Auto-discovered topics</span></div>', unsafe_allow_html=True)
            unique = list(set(st.session_state.cluster_labels))
            counts = [list(st.session_state.cluster_labels).count(c) for c in unique]
            labels = [st.session_state.topic_names.get(c, f"Cluster {c}") for c in unique]
            colors = ["#8B7FF0","#4CAF7D","#E5945B","#5BA4E5","#E57FAA","#4ECBA5"]
            fig, ax = plt.subplots(figsize=(5, 2.8), facecolor="#13131a")
            wedges, texts, autotexts = ax.pie(
                counts, labels=labels, autopct="%1.0f%%", colors=colors[:len(unique)],
                textprops={"color":"#aaa","fontsize":9}, pctdistance=0.75,
                wedgeprops={"linewidth": 1.5, "edgecolor": "#0e0e11"}
            )
            for at in autotexts: at.set_fontsize(8); at.set_color("#fff")
            ax.set_facecolor("#13131a")
            st.pyplot(fig)
            plt.close()

            # Topic pills
            st.markdown('<div class="cb-insight"><div class="cb-insight-title">🔖 Discovered topics</div><div class="cb-pill-row">', unsafe_allow_html=True)
            pill_colors = ["", "cb-pill-green", "cb-pill-orange", "cb-pill-blue"]
            pills = ""
            for i, (cid, name) in enumerate(st.session_state.topic_names.items()):
                cls = pill_colors[i % len(pill_colors)]
                pills += f'<span class="cb-pill {cls}">{name}</span>'
            st.markdown(pills + '</div></div>', unsafe_allow_html=True)

        # Uploaded documents
        if st.session_state.document_names:
            st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">📁 Indexed documents</span></div>', unsafe_allow_html=True)
            icons = ["📄","📋","📑","🗂️","📃","📜"]
            colors_bg = ["#2a2560","#0d1e35","#0d2e1a","#2e1e0d","#0d2e28"]
            for i, doc in enumerate(list(st.session_state.document_names)):
                bg = colors_bg[i % len(colors_bg)]
                ico = icons[i % len(icons)]
                st.markdown(f"""
                <div class="cb-doc" style="margin-bottom:8px">
                  <div style="display:flex;align-items:center;gap:12px">
                    <div class="cb-doc-icon" style="background:{bg}">{ico}</div>
                    <div style="flex:1">
                      <div class="cb-doc-name">{doc}</div>
                      <div class="cb-doc-meta">
                        <span class="cb-tag tag-doc">indexed</span>
                        Ready to query
                      </div>
                    </div>
                    <span style="font-size:11px;color:#4CAF7D">✓</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="cb-gap">
              <div class="cb-gap-icon">💡</div>
              <div class="cb-gap-text">
                <strong>No documents yet.</strong> Upload PDFs in the Upload tab to build your knowledge base. Company Brain supports any PDF — HR policies, technical docs, contracts, manuals.
              </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        # Recent query history
        st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🕑 Recent queries</span></div>', unsafe_allow_html=True)
        if st.session_state.query_history:
            for item in reversed(st.session_state.query_history[-8:]):
                score = item["score"]
                score_cls = "score-high" if score >= 0.7 else ("score-mid" if score >= 0.4 else "score-low")
                score_label = f"{int(score*100)}%"
                topic = item.get("topic", "—")
                st.markdown(f"""
                <div class="cb-query-item">
                  <div style="flex:1">
                    <div class="cb-query-q">💬 {item['q'][:72]}{'…' if len(item['q'])>72 else ''}</div>
                    <div class="cb-query-meta">🏷️ {topic}</div>
                  </div>
                  <span class="cb-query-score {score_cls}">{score_label}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:40px 0;color:#444;font-size:12px">
              <div style="font-size:28px;margin-bottom:8px">💬</div>
              No queries yet.<br>Ask a question in the <strong style="color:#666">Ask AI</strong> tab.
            </div>
            """, unsafe_allow_html=True)

        # Knowledge gaps summary
        if st.session_state.knowledge_gaps:
            st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
            st.markdown(f'<div class="cb-sec-hdr"><span class="cb-sec-title">⚠️ Knowledge gaps ({len(st.session_state.knowledge_gaps)})</span></div>', unsafe_allow_html=True)
            for gq in st.session_state.knowledge_gaps[-4:]:
                st.markdown(f"""
                <div class="cb-gap-item">
                  <span style="font-size:14px">⚠️</span>
                  <span class="cb-gap-q">{gq[:65]}{'…' if len(gq)>65 else ''}</span>
                </div>
                """, unsafe_allow_html=True)
            if st.button("View all gaps →", key="dash_gaps"):
                st.session_state.page = "gaps"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ASK AI (CHAT)
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    try:
        from utils.pdf_reader import extract_text_from_pdf
        from utils.llm import generate_answer_with_retry
        from utils.vector_store import store_chunks, get_all_chunks, search_cluster_chunks
        from utils.text_splitter import spit_text_into_chunks
        from utils.embeddings import create_embeddings, model as embed_model
        from utils.chat_memory import get_recent_chat
        from utils.keyword_search import keyword_search
    except ImportError:
        st.error("Utils not found. Make sure all utils/ files are in place.")
        st.stop()

    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    # Chat header
    st.markdown("""
    <div style="margin-bottom:16px">
      <div style="font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.4px">✨ Ask AI</div>
      <div style="font-size:12px;color:#555;margin-top:3px">Ask anything about your uploaded documents. Company Brain searches across all indexed content.</div>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.document_names) == 0:
        st.markdown("""
        <div class="cb-gap">
          <div class="cb-gap-icon">⚠️</div>
          <div class="cb-gap-text"><strong>No documents uploaded yet.</strong> Go to the Upload tab first to add PDFs before asking questions.</div>
        </div>
        """, unsafe_allow_html=True)

    # Render chat history
    for message in st.session_state.messages:
        role = message["role"]
        with st.chat_message(role, avatar="🧠" if role == "assistant" else "👤"):
            st.markdown(message["content"])
            if role == "assistant" and "score" in message:
                score = message["score"]
                attempts = message.get("attempts", 1)
                reason = message.get("reason", "")
                with st.expander("📊 Answer quality"):
                    st.progress(score, text=f"Confidence: {score:.0%}")
                    st.caption(f"🔁 Attempts: {attempts} · {reason}")

    user_query = st.chat_input("Ask a question about your documents...")

    if user_query:
        if len(st.session_state.document_names) == 0:
            st.warning("Please upload a PDF first.")
            st.stop()

        chat_history = get_recent_chat(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        if st.session_state.kmeans is None:
            st.error("No clustering model available. Please re-upload a document.")
            st.stop()

        query_embedding = embed_model.encode(user_query, convert_to_numpy=True)
        query_embedding = query_embedding.astype(np.float64).reshape(1, -1)

        query_cluster = st.session_state.kmeans.predict(query_embedding)[0]
        topic_name = st.session_state.topic_names.get(int(query_cluster), f"Cluster {query_cluster}")

        st.markdown(f'<div class="cb-topic-pill">🏷️ Detected topic: {topic_name}</div>', unsafe_allow_html=True)

        results = search_cluster_chunks(query_embedding, query_cluster, k=3)
        all_chunks = get_all_chunks()
        keyword_chunks = keyword_search(user_query, all_chunks, k=2)

        top_chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        combined_chunks = list(top_chunks)
        for chunk in keyword_chunks:
            if chunk not in combined_chunks:
                combined_chunks.append(chunk)

        context = ""
        for i, chunk in enumerate(combined_chunks):
            source = "keyword search"
            if i < len(metadatas) and metadatas[i]:
                source = metadatas[i].get("source", "unknown")
            context += f"{chunk} (Source: {source})\n\n"

        final_context = f"""
        conversation history:
        {chat_history}

        knowledge base:
        {context}
        """

        with st.spinner("Thinking..."):
            answer, score, attempts, reason = generate_answer_with_retry(
                final_context, user_query, max_retries=3
            )

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(answer)
            with st.expander("📊 Answer quality"):
                st.progress(score, text=f"Confidence: {score:.0%}")
                st.caption(f"🔁 Attempts: {attempts} · {reason}")

        # Store query history
        st.session_state.query_history.append({
            "q": user_query, "score": score, "topic": topic_name,
        })

        # Track knowledge gaps (low confidence)
        if score < 0.4:
            if user_query not in st.session_state.knowledge_gaps:
                st.session_state.knowledge_gaps.append(user_query)

        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "score": score, "attempts": attempts, "reason": reason
        })

    if st.session_state.messages:
        if st.button("🧹 Clear chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "upload":
    try:
        from utils.pdf_reader import extract_text_from_pdf
        from utils.vector_store import store_chunks
        from utils.text_splitter import spit_text_into_chunks
        from utils.embeddings import create_embeddings
        from utils.topic_clustering import cluster_chunks
        from utils.topic_namer import generate_topic_name
    except ImportError:
        st.error("Utils not found.")
        st.stop()

    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:20px">
      <div style="font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.4px">📤 Upload Documents</div>
      <div style="font-size:12px;color:#555;margin-top:3px">Add PDFs to your knowledge base. Company Brain will extract text, split into chunks, embed with AI, and cluster by topic automatically.</div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline steps visualization
    st.markdown("""
    <div class="cb-steps" style="margin-bottom:20px">
      <div class="cb-step">
        <div class="cb-step-num">STEP 01</div>
        <div style="font-size:18px;margin-bottom:8px">📄</div>
        <h4>PDF Extraction</h4>
        <p>Text is extracted from every page of your PDF using PyPDF.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 02</div>
        <div style="font-size:18px;margin-bottom:8px">✂️</div>
        <h4>Chunking</h4>
        <p>Text is split into 1,000-character chunks with 200-character overlap for context continuity.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 03</div>
        <div style="font-size:18px;margin-bottom:8px">🔢</div>
        <h4>Embedding</h4>
        <p>Each chunk is encoded into a 384-dimension vector using all-MiniLM-L6-v2.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 04</div>
        <div style="font-size:18px;margin-bottom:8px">🏷️</div>
        <h4>Topic Clustering</h4>
        <p>K-Means groups chunks into topics. OpenRouter AI names each cluster automatically.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    doc_count = len(st.session_state.document_names)
    topic_count = len(st.session_state.topic_names)
    st.markdown(f"""
    <div class="cb-stats" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px">
      <div class="cb-stat"><div class="cb-stat-num" style="color:#a78bfa">{doc_count}</div><div class="cb-stat-label">Files indexed</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#4CAF7D">{topic_count}</div><div class="cb-stat-label">Topics found</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#E5945B">{len(st.session_state.processed_files)}</div><div class="cb-stat-label">PDFs processed</div></div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDFs here or click to browse",
        type=["pdf"], accept_multiple_files=True, label_visibility="visible"
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name in st.session_state.processed_files:
                st.markdown(f"""
                <div class="cb-file-item">
                  <div class="cb-file-icon">📄</div>
                  <div class="cb-file-info">
                    <div class="cb-file-name">{uploaded_file.name}</div>
                    <div class="cb-file-sub">Already indexed — no re-processing needed</div>
                    <div class="cb-prog-bg"><div class="cb-prog" style="width:100%;background:#4CAF7D"></div></div>
                  </div>
                  <span class="cb-status status-indexed">Indexed</span>
                </div>
                """, unsafe_allow_html=True)
                continue

            st.markdown(f"""
            <div class="cb-file-item">
              <div class="cb-file-icon">📄</div>
              <div class="cb-file-info">
                <div class="cb-file-name">{uploaded_file.name}</div>
                <div class="cb-file-sub">Processing — extracting, chunking, embedding...</div>
                <div class="cb-prog-bg"><div class="cb-prog" style="width:55%;background:#8B7FF0"></div></div>
              </div>
              <span class="cb-status status-indexing">Indexing</span>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner(f"Indexing {uploaded_file.name}..."):
                text = extract_text_from_pdf(uploaded_file)
                chunks = spit_text_into_chunks(text)
                embeddings = create_embeddings(chunks)
                labels, kmeans = cluster_chunks(embeddings, n_clusters=4)
                st.session_state.cluster_labels = list(labels)
                st.session_state.kmeans = kmeans

                chunk_cluster_map = {i: int(label) for i, label in enumerate(labels)}
                st.session_state.chunk_cluster_map = chunk_cluster_map

                topic_names = {}
                for cluster_id in set(labels):
                    cluster_chunks_list = [chunks[i] for i in range(len(chunks)) if labels[i] == cluster_id]
                    time.sleep(2)
                    topic_names[cluster_id] = generate_topic_name(cluster_chunks_list)
                st.session_state.topic_names = topic_names
                st.session_state.total_chunks_stored += len(chunks)

                store_chunks(chunks, embeddings, uploaded_file.name, labels)
                st.session_state.document_names.add(uploaded_file.name)
                st.session_state.processed_files.add(uploaded_file.name)

            st.success(f"✅ {uploaded_file.name} indexed — {len(chunks)} chunks · {len(topic_names)} topics discovered")

            # Show discovered topics
            if topic_names:
                pills = " ".join([f'<span class="cb-pill">{n}</span>' for n in topic_names.values()])
                st.markdown(f'<div style="margin-top:4px;margin-bottom:16px"><div class="cb-pill-row">{pills}</div></div>', unsafe_allow_html=True)

    # Indexed documents list
    if st.session_state.document_names:
        st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
        st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">📁 Indexed documents</span></div>', unsafe_allow_html=True)
        for doc in st.session_state.document_names:
            st.markdown(f"""
            <div class="cb-file-item">
              <div class="cb-file-icon">📄</div>
              <div class="cb-file-info">
                <div class="cb-file-name">{doc}</div>
                <div class="cb-file-sub">Chunked · Embedded · Clustered · Ready to query</div>
                <div class="cb-prog-bg"><div class="cb-prog" style="width:100%;background:#4CAF7D"></div></div>
              </div>
              <span class="cb-status status-indexed">Indexed</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: KNOWLEDGE GAPS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "gaps":
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:20px">
      <div style="font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.4px">⚠️ Knowledge Gaps</div>
      <div style="font-size:12px;color:#555;margin-top:3px">
        Questions Company Brain couldn't answer confidently — these indicate missing documents in your knowledge base.
      </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="medium")

    with left:
        if st.session_state.knowledge_gaps:
            st.markdown(f"""
            <div class="cb-gap" style="margin-bottom:20px">
              <div class="cb-gap-icon">⚠️</div>
              <div class="cb-gap-text">
                <strong>{len(st.session_state.knowledge_gaps)} unanswered question{"s" if len(st.session_state.knowledge_gaps)!=1 else ""} detected.</strong>
                These questions returned low-confidence answers. Consider uploading more relevant documents to fill these gaps.
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">Unanswered questions</span></div>', unsafe_allow_html=True)
            for i, gq in enumerate(st.session_state.knowledge_gaps):
                st.markdown(f"""
                <div class="cb-query-item" style="border-color:#3a2e10">
                  <span style="font-size:18px">⚠️</span>
                  <div style="flex:1">
                    <div class="cb-query-q" style="color:#a08040">{gq}</div>
                    <div class="cb-query-meta" style="color:#5a4020">Low confidence · No matching document found</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑️ Clear knowledge gaps", type="secondary"):
                st.session_state.knowledge_gaps = []
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 0;color:#444">
              <div style="font-size:40px;margin-bottom:12px">✅</div>
              <div style="font-size:14px;font-weight:600;color:#666;margin-bottom:6px">No knowledge gaps found</div>
              <div style="font-size:12px">All questions so far were answered with high confidence.</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">💡 How to fix gaps</span></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="cb-insight">
          <div class="cb-insight-title">📋 Recommended actions</div>
          <div style="font-size:12px;color:#666;line-height:1.9">
            <div style="margin-bottom:8px">📄 <strong style="color:#aaa">Upload related PDFs</strong><br>Add documents that cover the unanswered topics above.</div>
            <div style="margin-bottom:8px">🔍 <strong style="color:#aaa">Check document quality</strong><br>Make sure uploaded PDFs have readable, searchable text (not scanned images).</div>
            <div>🔢 <strong style="color:#aaa">Increase clusters</strong><br>If your documents cover many topics, increase the cluster count in settings for better retrieval.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Query confidence histogram
        if st.session_state.query_history:
            st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">📊 Confidence distribution</span></div>', unsafe_allow_html=True)
            scores = [q["score"] for q in st.session_state.query_history]
            fig, ax = plt.subplots(figsize=(4, 2), facecolor="#13131a")
            ax.hist(scores, bins=10, color="#6B5CE7", edgecolor="#0e0e11", range=(0,1))
            ax.set_facecolor("#13131a")
            ax.tick_params(colors="#555", labelsize=8)
            ax.spines[:].set_color("#232330")
            ax.set_xlabel("Confidence score", color="#555", fontsize=8)
            ax.set_ylabel("# queries", color="#555", fontsize=8)
            st.pyplot(fig)
            plt.close()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FEATURES
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "features":
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-hero" style="margin-bottom:28px">
      <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>RAG · Semantic Search · OpenRouter AI · DeepEval</div>
      <h1>How <span>Company Brain</span> works</h1>
      <p>A full Retrieval-Augmented Generation (RAG) pipeline — from raw PDF to intelligent, context-aware answers. Built with sentence-transformers, ChromaDB, K-Means clustering, OpenRouter, and DeepEval scoring.</p>
    </div>
    """, unsafe_allow_html=True)

    # Core features
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🚀 Core features</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-features">
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#1e1a35">🔢</div>
        <h3>Semantic Vector Search</h3>
        <p>Documents are embedded using <strong style="color:#aaa">all-MiniLM-L6-v2</strong> into 384-dimensional vectors. Queries are matched by cosine similarity — finding meaning, not just keywords.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d1e35">🏷️</div>
        <h3>Auto Topic Clustering</h3>
        <p><strong style="color:#aaa">K-Means clustering</strong> groups document chunks into topics automatically. OpenRouter AI then names each cluster in plain language — no manual tagging needed.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d2e1a">🔍</div>
        <h3>Hybrid Retrieval</h3>
        <p>Combines <strong style="color:#aaa">vector similarity search</strong> and <strong style="color:#aaa">BM25-style keyword search</strong> for maximum recall. The best of both worlds in every query.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#2e1e0d">💬</div>
        <h3>Conversation Memory</h3>
        <p>Company Brain remembers the last <strong style="color:#aaa">4 exchanges</strong> in your conversation, enabling natural follow-up questions without losing context.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d2e28">⚡</div>
        <h3>Answer Quality Scoring</h3>
        <p>Every response is scored for confidence and retried up to <strong style="color:#aaa">3 times</strong> if quality is low — so you always get the best possible answer.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#2a1030">⚠️</div>
        <h3>Knowledge Gap Detection</h3>
        <p>Low-confidence answers are automatically flagged as <strong style="color:#aaa">knowledge gaps</strong> — showing you exactly which topics need more documents.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tech stack
    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🛠️ Tech stack</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-features" style="grid-template-columns:repeat(4,1fr)">
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#1e1a35;font-size:22px">🤗</div>
        <h3>Sentence Transformers</h3>
        <p><code style="color:#a78bfa;font-size:10px">all-MiniLM-L6-v2</code><br>Creates dense semantic embeddings from text chunks.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d1e35;font-size:22px">🗄️</div>
        <h3>ChromaDB</h3>
        <p>Persistent vector store for fast approximate nearest-neighbor search across all document embeddings.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d2e1a;font-size:22px">🤖</div>
        <h3>OpenRouter AI</h3>
        <p>Flexible LLM gateway for answer generation and topic naming — swap models without changing code.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#2a1030;font-size:22px">📊</div>
        <h3>DeepEval</h3>
        <p><code style="color:#E57FAA;font-size:10px">FaithfulnessMetric + AnswerRelevancyMetric</code><br>Scores every answer for quality with a dedicated judge model.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#2e1e0d;font-size:22px">📐</div>
        <h3>LangChain Splitter</h3>
        <p><code style="color:#E5945B;font-size:10px">RecursiveCharacterTextSplitter</code><br>Splits docs into 1,000-char chunks with 200-char overlap.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # RAG pipeline diagram
    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🔄 RAG pipeline</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-pipeline-wrap">
      <div class="cb-pipeline">
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">📄</div>
          <div class="cb-pipeline-label">PDF Upload</div>
          <div class="cb-pipeline-sub">PyPDF extraction</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">✂️</div>
          <div class="cb-pipeline-label">Chunking</div>
          <div class="cb-pipeline-sub">1000 chars / 200 overlap</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">🔢</div>
          <div class="cb-pipeline-label">Embedding</div>
          <div class="cb-pipeline-sub">384-dim vectors</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">🏷️</div>
          <div class="cb-pipeline-label">Clustering</div>
          <div class="cb-pipeline-sub">K-Means + AI naming</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">🗄️</div>
          <div class="cb-pipeline-label">ChromaDB</div>
          <div class="cb-pipeline-sub">Persistent storage</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">🤖</div>
          <div class="cb-pipeline-label">OpenRouter AI</div>
          <div class="cb-pipeline-sub">Answer generation</div>
        </div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step">
          <div class="cb-pipeline-icon">📊</div>
          <div class="cb-pipeline-label">DeepEval</div>
          <div class="cb-pipeline-sub">Faithfulness scoring</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Use cases
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">💼 Use cases</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-features" style="grid-template-columns:repeat(3,1fr)">
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d2e1a;font-size:20px">🏢</div>
        <h3>HR & Policy</h3>
        <p>Upload employee handbooks, leave policies, and HR FAQs. Let employees ask questions in plain language instead of searching through PDFs.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#0d1e35;font-size:20px">⚙️</div>
        <h3>Technical Docs</h3>
        <p>Index API references, architecture docs, and runbooks. Developers get instant answers without switching contexts.</p>
      </div>
      <div class="cb-feature">
        <div class="cb-feature-icon" style="background:#2a1030;font-size:20px">⚖️</div>
        <h3>Legal & Compliance</h3>
        <p>Upload contracts, SOPs, and compliance docs. Ask about specific clauses, obligations, and deadlines instantly.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)