import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Company Brain", layout="wide", page_icon="🧠")

# ── Helper functions: copy button, confidence bar, sources, feedback ─────────

def copy_button(text: str, key: str):
    safe_text = text.replace("`", "\\`").replace("\\", "\\\\").replace("\n", "\\n")
    html_code = f"""
    <textarea id="copy-text-{key}" style="position:absolute;left:-9999px;">{text}</textarea>
    <button id="copy-btn-{key}" style="
        background:#1a1a24;border:0.5px solid #2e2e42;color:#999;
        font-size:11px;padding:5px 12px;border-radius:8px;cursor:pointer;
        font-family:-apple-system,sans-serif;">
        📋 Copy answer
    </button>
    <script>
        document.getElementById("copy-btn-{key}").onclick = function() {{
            const textarea = document.getElementById("copy-text-{key}");
            textarea.style.position = "fixed";
            textarea.style.top = "0";
            textarea.focus();
            textarea.select();
            try {{
                document.execCommand("copy");
                this.innerText = "✅ Copied!";
            }} catch (err) {{
                this.innerText = "❌ Failed";
            }}
            textarea.style.position = "absolute";
            textarea.style.left = "-9999px";
            setTimeout(() => this.innerText = "📋 Copy answer", 1500);
        }};
    </script>
    """
    components.html(html_code, height=40)


def confidence_bar_html(score: float) -> str:
    pct = int(score * 100)
    if score >= 0.7:
        color, label = "#4CAF7D", "High confidence"
    elif score >= 0.4:
        color, label = "#E5945B", "Medium confidence"
    else:
        color, label = "#E57070", "Low confidence"
    return f"""
    <div style="margin:8px 0 4px;">
      <div style="display:flex;justify-content:space-between;font-size:11px;color:#777;margin-bottom:4px;">
        <span>{label}</span><span style="font-weight:600;color:{color}">{pct}%</span>
      </div>
      <div style="height:6px;background:#232330;border-radius:4px;overflow:hidden;">
        <div style="height:100%;width:{pct}%;background:{color};border-radius:4px;"></div>
      </div>
    </div>
    """


def render_sources(sources: list, key_prefix: str):
    if not sources:
        return
    with st.expander(f"📚 Sources ({len(sources)})"):
        for s in sources:
            st.markdown(f"""
            <div style="background:#13131a;border:0.5px solid #232330;border-radius:8px;
                        padding:10px 14px;margin-bottom:6px;">
              <div style="font-size:11px;color:#a78bfa;font-weight:600;margin-bottom:4px;">
                📄 {s['source']}
              </div>
              <div style="font-size:12px;color:#888;line-height:1.5;">
                {s['snippet']}
              </div>
            </div>
            """, unsafe_allow_html=True)


def feedback_widget(msg_index: int):
    fb_key = f"feedback_{msg_index}"
    current = st.session_state.messages[msg_index].get("feedback")
    col1, col2, col3 = st.columns([1, 1, 10])
    with col1:
        if st.button("👍" if current != "up" else "✅👍", key=f"{fb_key}_up"):
            st.session_state.messages[msg_index]["feedback"] = "up"
            st.rerun()
    with col2:
        if st.button("👎" if current != "down" else "✅👎", key=f"{fb_key}_down"):
            st.session_state.messages[msg_index]["feedback"] = "down"
            st.rerun()
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 0 !important; max-width: 100% !important;}

body, .stApp { background: #0e0e11 !important; color: #ccc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

section[data-testid="stSidebar"] {
    background: #13131a !important;
    border-right: 0.5px solid #232330 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 18px; }
.cb-sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 0 4px 18px; margin-bottom: 6px;
    border-bottom: 0.5px solid #232330;
}
.cb-sidebar-section-label {
    font-size: 10px; color: #444; text-transform: uppercase; letter-spacing: 0.8px;
    font-weight: 600; margin: 16px 4px 8px;
}
.cb-sidebar-footer {
    margin-top: 18px; padding-top: 14px; border-top: 0.5px solid #232330;
}
.cb-sidebar-footer-row {
    display: flex; justify-content: space-between; font-size: 11px; color: #555;
    padding: 5px 4px;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    background: transparent !important; border: 0.5px solid transparent !important;
    color: #888 !important; font-size: 13px !important; font-weight: 500 !important;
    justify-content: flex-start !important; padding: 9px 14px !important;
    border-radius: 8px !important; box-shadow: none !important; transition: all .15s !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
    background: #1a1a24 !important; color: #ccc !important; border-color: #2e2e42 !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg,#6B5CE7,#8b5cf6) !important; color: #fff !important;
    box-shadow: 0 2px 12px #6B5CE744 !important; border-color: transparent !important;
}
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
.cb-content { padding: 24px 28px; }
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
.cb-stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px; }
.cb-stat {
    background: #13131a; border: 0.5px solid #232330; border-radius: 12px; padding: 18px 20px;
    transition: border-color .2s;
}
.cb-stat:hover { border-color: #3a3a50; }
.cb-stat-num { font-size: 32px; font-weight: 700; margin-bottom: 4px; letter-spacing: -1px; }
.cb-stat-label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
.cb-stat-change { font-size: 10px; color: #4CAF7D; margin-top: 6px; }
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
.cb-gap {
    background: #1a150d; border: 0.5px solid #3a2e10; border-radius: 12px;
    padding: 14px 18px; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 20px;
}
.cb-gap-icon { width: 30px; height: 30px; background: #2a2210; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 14px; }
.cb-gap-text { font-size: 12px; color: #a08040; line-height: 1.6; }
.cb-gap-text strong { color: #d4a840; }
.cb-gap-item {
    background: #1a150d; border: 0.5px solid #3a2e10; border-radius: 9px;
    padding: 10px 14px; margin-bottom: 7px; display: flex; align-items: center; gap: 10px;
}
.cb-gap-q { font-size: 12px; color: #a08040; flex: 1; }
.cb-topic-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1e1a35; border: 0.5px solid #3a3060; border-radius: 6px;
    padding: 5px 11px; font-size: 11px; color: #8B7FF0; margin-bottom: 6px;
}
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
.stChatMessage { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 12px !important; }
.stChatInput > div { background: #1a1a24 !important; border: 0.5px solid #2e2e42 !important; border-radius: 10px !important; }
.stChatInput textarea { color: #ccc !important; background: transparent !important; }
.stFileUploader { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 10px !important; }
div[data-testid="stFileUploadDropzone"] { background: #16161f !important; border: 1.5px dashed #2e2e42 !important; border-radius: 10px !important; }
.stProgress > div > div { background: linear-gradient(90deg, #6B5CE7, #a78bfa) !important; }
.stExpander { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 8px !important; }
.stAlert { border-radius: 8px !important; }
.cb-sec-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.cb-sec-title { font-size: 14px; color: #bbb; font-weight: 600; letter-spacing: -0.2px; }
.cb-sec-sub { font-size: 11px; color: #555; }
.cb-divider { border: none; border-top: 0.5px solid #1e1e2a; margin: 24px 0; }
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
.cb-pipeline-wrap {
    background: #13131a; border: 0.5px solid #232330; border-radius: 14px;
    padding: 28px 32px; margin-bottom: 24px;
}
.cb-pipeline {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
}
.cb-pipeline-step { text-align: center; flex: 1; min-width: 90px; }
.cb-pipeline-icon { font-size: 28px; margin-bottom: 6px; }
.cb-pipeline-label { font-size: 12px; font-weight: 600; color: #ccc; margin-bottom: 3px; }
.cb-pipeline-sub { font-size: 10px; color: #555; }
.cb-pipeline-arrow { color: #333; font-size: 20px; flex-shrink: 0; }
.cb-welcome { text-align: center; padding: 28px 0 20px; }
.cb-welcome-icon {
    width: 60px; height: 60px;
    background: linear-gradient(135deg,#6B5CE7,#a78bfa);
    border-radius: 18px; display: inline-flex; align-items: center;
    justify-content: center; font-size: 28px; margin-bottom: 16px;
    box-shadow: 0 0 32px #6B5CE733;
}
.cb-welcome h2 { font-size: 22px; font-weight: 700; color: #fff; letter-spacing: -0.5px; margin: 0 0 8px; }
.cb-welcome p  { font-size: 13px; color: #555; margin: 0; }
.cb-sugg-label {
    font-size: 10px; color: #444; text-transform: uppercase;
    letter-spacing: 0.8px; font-weight: 600; margin: 24px 0 12px;
}
div[data-testid="stButton"].chip-btn > button {
    background: #13131a !important;
    border: 0.5px solid #2a2a3a !important;
    border-radius: 12px !important;
    color: #999 !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 13px 16px !important;
    line-height: 1.55 !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 52px !important;
    box-shadow: none !important;
    transition: all .15s !important;
}
div[data-testid="stButton"].chip-btn > button:hover {
    background: #1a1a28 !important;
    border-color: #6B5CE7 !important;
    color: #ddd !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px #6B5CE722 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "processed_files": set(), "document_names": set(),
    "cluster_labels": None, "topic_names": {}, "chunk_cluster_map": {},
    "kmeans": None, "page": "dashboard",
    "query_history": [],
    "knowledge_gaps": [],
    "total_chunks_stored": 0,
    "pdf_suggestions": [],
    "doc_embeddings": {},
    "doc_chunk_counts": {},
    "doc_topic_maps": {},
    "doc_summaries":{},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="cb-sidebar-logo">
      <div class="cb-logo-icon">🧠</div>
      <div>
        <div class="cb-logo-text">Company Brain</div>
        <div class="cb-logo-sub">Knowledge Intelligence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cb-sidebar-section-label">Navigate</div>', unsafe_allow_html=True)

    nav_items = [
        ("dashboard", "📊  Dashboard"),
        ("chat",      "✨  Ask AI"),
        ("upload",    "📤  Upload"),
        ("gaps",      "🔍  Knowledge Gaps"),
        ("features",  "⚡  Features"),
    ]
    for key, label in nav_items:
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state.page == key else "secondary",
                     key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()

    st.markdown(f"""
    <div class="cb-sidebar-footer">
      <div class="cb-sidebar-footer-row"><span>📄 Documents</span><span>{len(st.session_state.document_names)}</span></div>
      <div class="cb-sidebar-footer-row"><span>🏷️ Topics</span><span>{len(st.session_state.topic_names)}</span></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    doc_count = len(st.session_state.document_names)
    if doc_count == 0:
        st.markdown("""
        <div class="cb-hero">
          <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>RAG-powered · Semantic Search · Topic Clustering</div>
          <h1>Your documents.<br><span>Intelligent answers.</span></h1>
          <p>Company Brain turns your PDFs into a searchable knowledge base — powered by vector embeddings, topic clustering, and Groq AI. Upload once, ask anything.</p>
        </div>
        """, unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("📤 Upload your first PDF →", type="primary", use_container_width=True, key="dash_upload_btn"):
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
            if st.button("✨ Ask a question →", type="primary", use_container_width=True, key="dash_ask_btn"):
                st.session_state.page = "chat"; st.rerun()

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

    left, right = st.columns([3, 2], gap="medium")

    with left:
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

            st.markdown('<div class="cb-insight"><div class="cb-insight-title">🔖 Discovered topics</div><div class="cb-pill-row">', unsafe_allow_html=True)
            pill_colors = ["", "cb-pill-green", "cb-pill-orange", "cb-pill-blue"]
            pills = ""
            for i, (cid, name) in enumerate(st.session_state.topic_names.items()):
                cls = pill_colors[i % len(pill_colors)]
                pills += f'<span class="cb-pill {cls}">{name}</span>'
            st.markdown(pills + '</div></div>', unsafe_allow_html=True)

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
                <strong>No documents yet.</strong> Upload PDFs in the Upload tab to build your knowledge base.
              </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
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
# PAGE: ASK AI (CHAT)  — single, clean block
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
        from utils.suggestion_generator import generate_followup_suggestions
    except ImportError:
        st.error("Utils not found. Make sure all utils/ files are in place.")
        st.stop()

    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:16px">
      <div style="font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.4px">✨ Ask AI</div>
      <div style="font-size:12px;color:#555;margin-top:3px">Ask anything about your uploaded documents.</div>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.document_names) == 0:
        st.markdown("""
        <div class="cb-gap">
          <div class="cb-gap-icon">⚠️</div>
          <div class="cb-gap-text"><strong>No documents uploaded yet.</strong> Go to the Upload tab first to add PDFs before asking questions.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Welcome screen (only when chat is empty) ──────────────────────────────
    if not st.session_state.messages:
        st.markdown("""
        <div class="cb-welcome">
          <div class="cb-welcome-icon">🧠</div>
          <h2>What would you like to know?</h2>
          <p>Pick a suggestion or type your own question below.</p>
        </div>
        """, unsafe_allow_html=True)

        suggestions = st.session_state.pdf_suggestions
        if suggestions:
            display = suggestions[:4]
            st.markdown('<div class="cb-sugg-label">Suggested from your documents</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2, gap="small")
            for idx, question in enumerate(display):
                with (col1 if idx % 2 == 0 else col2):
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    if st.button(f"💬  {question}", key=f"welcome_chip_{idx}", use_container_width=True):
                        st.session_state["_chip_query"] = question
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            if len(suggestions) > 4:
                with st.expander(f"Show {len(suggestions) - 4} more suggestions"):
                    col3, col4 = st.columns(2, gap="small")
                    for idx, question in enumerate(suggestions[4:]):
                        with (col3 if idx % 2 == 0 else col4):
                            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                            if st.button(f"💬  {question}", key=f"welcome_chip_more_{idx}", use_container_width=True):
                                st.session_state["_chip_query"] = question
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cb-sugg-label">Upload a PDF to see personalised suggestions</div>', unsafe_allow_html=True)
            placeholder_qs = [
                "What are the main topics in this document?",
                "Summarize the key findings.",
                "What processes or procedures are described?",
                "Are there any important dates or deadlines?",
            ]
            col1, col2 = st.columns(2, gap="small")
            for idx, question in enumerate(placeholder_qs):
                with (col1 if idx % 2 == 0 else col2):
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    st.button(f"💬  {question}", key=f"placeholder_{idx}",
                              use_container_width=True, disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)

    # ── Pick up chip click from session state ─────────────────────────────────
    chip_query = st.session_state.pop("_chip_query", None)

    # ── Render existing chat history ──────────────────────────────────────────
    messages = st.session_state.messages
    for i, message in enumerate(messages):
        role = message["role"]
        with st.chat_message(role, avatar="🧠" if role == "assistant" else "👤"):
            st.markdown(message["content"])
            if role == "assistant":
                if "score" in message:
                    st.markdown(confidence_bar_html(message["score"]), unsafe_allow_html=True)
                copy_button(message["content"], key=f"hist_{i}")
                if "sources" in message:
                    render_sources(message["sources"], key_prefix=f"hist_{i}")
                feedback_widget(i)
                if "score" in message:
                    with st.expander(f"🔁 {message.get('attempts',1)} attempt(s) · details"):
                        st.caption(message.get("reason", ""))
        # Show stored follow-up chips after every past assistant message
        # (skip the last message — it gets chips rendered fresh below)
        if role == "assistant" and "followups" in message and i < len(messages) - 1:
            followups = message["followups"]
            if followups:
                st.markdown('<div class="cb-sugg-label" style="margin-top:4px">💡 Follow-up suggestions</div>', unsafe_allow_html=True)
                cols = st.columns(len(followups), gap="small")
                for fi, fq in enumerate(followups):
                    with cols[fi]:
                        st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                        if st.button(f"💬  {fq}", key=f"hist_followup_{i}_{fi}", use_container_width=True):
                            st.session_state["_chip_query"] = fq
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    # Show follow-up chips for the very last assistant message too (if no new query yet)
    if messages and messages[-1]["role"] == "assistant" and "followups" in messages[-1]:
        last_followups = messages[-1]["followups"]
        if last_followups and chip_query is None:
            st.markdown('<div class="cb-sugg-label" style="margin-top:4px">💡 Follow-up suggestions</div>', unsafe_allow_html=True)
            cols = st.columns(len(last_followups), gap="small")
            for fi, fq in enumerate(last_followups):
                with cols[fi]:
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    if st.button(f"💬  {fq}", key=f"last_followup_{fi}", use_container_width=True):
                        st.session_state["_chip_query"] = fq
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # ── Single chat input ─────────────────────────────────────────────────────
    user_query = st.chat_input("Ask a question about your documents...", key="chat_input_main")
    if chip_query:
        user_query = chip_query  # chip click overrides typed input

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
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)

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
        sources_used = []
        for idx, chunk in enumerate(combined_chunks):
            source = "keyword search"
            if idx < len(metadatas) and metadatas[idx]:
                source = metadatas[idx].get("source", "unknown")
            context += f"{chunk} (Source: {source})\n\n"
            sources_used.append({
                "source": source,
                "snippet": chunk[:180] + ("…" if len(chunk) > 180 else "")
            })

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

        with st.spinner("Generating follow-up suggestions..."):
            followups = generate_followup_suggestions(
                last_question=user_query,
                last_answer=answer,
                topic_name=topic_name,
                n=3,
            )

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(answer)
            st.markdown(confidence_bar_html(score), unsafe_allow_html=True)
            copy_button(answer, key=f"new_{len(st.session_state.messages)}")
            render_sources(sources_used, key_prefix=f"new_{len(st.session_state.messages)}")
            with st.expander(f"🔁 {attempts} attempt(s) · details"):
                st.caption(reason)

        # Show fresh follow-up chips right after the new answer
        if followups:
            st.markdown('<div class="cb-sugg-label" style="margin-top:4px">💡 Follow-up suggestions</div>', unsafe_allow_html=True)
            cols = st.columns(len(followups), gap="small")
            for fi, fq in enumerate(followups):
                with cols[fi]:
                    st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
                    if st.button(f"💬  {fq}", key=f"new_followup_{fi}", use_container_width=True):
                        st.session_state["_chip_query"] = fq
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Persist everything
        st.session_state.query_history.append({"q": user_query, "score": score, "topic": topic_name})

        if score < 0.5 and user_query not in st.session_state.knowledge_gaps:
            st.session_state.knowledge_gaps.append(user_query)

        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "score": score, "attempts": attempts, "reason": reason,
            "followups": followups, "sources":sources_used,
        })
        feedback_widget(len(st.session_state.messages)-1)

    if st.session_state.messages:
        if st.button("🧹 Clear chat", key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "upload":
    try:
        from utils.pdf_reader import extract_text_from_pdf
        from utils.url_reader import extract_text_from_url
        from utils.vector_store import store_chunks
        from utils.text_splitter import spit_text_into_chunks
        from utils.embeddings import create_embeddings
        from utils.topic_clustering import cluster_chunks
        from utils.suggestion_generator import generate_suggestions
        from utils.topic_namer import generate_topic_name
        from utils.summarizer import summarize_document
        
    except ImportError:
        st.error("Utils not found.")
        st.stop()

    st.markdown("""
    <style>
    div[data-testid="stTabs"] button {
        font-size: 13px !important; font-weight: 500 !important;
        color: #666 !important; border-radius: 8px 8px 0 0 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #a78bfa !important; border-bottom-color: #6B5CE7 !important;
    }
    .cb-url-box {
        background: #13131a; border: 0.5px solid #2e2e42; border-radius: 12px;
        padding: 20px 22px; margin-bottom: 16px;
    }
    .cb-url-box-title { font-size: 13px; font-weight: 600; color: #bbb; margin-bottom: 6px; }
    .cb-url-box-sub   { font-size: 11px; color: #555; margin-bottom: 14px; line-height: 1.6; }
    .cb-url-examples  { font-size: 11px; color: #444; margin-top: 10px; line-height: 1.8; }
    .cb-url-examples span { color: #6B5CE7; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:20px">
      <div style="font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.4px">📤 Upload Documents</div>
      <div style="font-size:12px;color:#555;margin-top:3px">
        Add PDFs or paste a URL. Company Brain extracts text, chunks it, embeds with AI, and clusters by topic.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-steps" style="margin-bottom:20px">
      <div class="cb-step">
        <div class="cb-step-num">STEP 01</div>
        <div style="font-size:18px;margin-bottom:8px">📄</div>
        <h4>Text Extraction</h4>
        <p>Text pulled from PDF pages or fetched directly from a URL or web page.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 02</div>
        <div style="font-size:18px;margin-bottom:8px">✂️</div>
        <h4>Chunking</h4>
        <p>Split into 1,000-char chunks with 200-char overlap for context continuity.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 03</div>
        <div style="font-size:18px;margin-bottom:8px">🔢</div>
        <h4>Embedding</h4>
        <p>Each chunk encoded into a 384-dim vector using all-MiniLM-L6-v2.</p>
        <span class="cb-step-arrow">→</span>
      </div>
      <div class="cb-step">
        <div class="cb-step-num">STEP 04</div>
        <div style="font-size:18px;margin-bottom:8px">🏷️</div>
        <h4>Topic Clustering</h4>
        <p>K-Means groups chunks into topics. OpenRouter AI names each cluster.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    doc_count   = len(st.session_state.document_names)
    topic_count = len(st.session_state.topic_names)
    total_chunks = sum(st.session_state.doc_chunk_counts.values()) if st.session_state.doc_chunk_counts else 0

    st.markdown(f"""
    <div class="cb-stats" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px">
      <div class="cb-stat"><div class="cb-stat-num" style="color:#a78bfa">{doc_count}</div><div class="cb-stat-label">Sources indexed</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#4CAF7D">{topic_count}</div><div class="cb-stat-label">Topics found</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#E5945B">{total_chunks}</div><div class="cb-stat-label">Total chunks stored</div></div>
    </div>
    """, unsafe_allow_html=True)

    def _index_text(text: str, source_name: str):
        chunks     = spit_text_into_chunks(text)
        embeddings = create_embeddings(chunks)
        labels, kmeans = cluster_chunks(embeddings, n_clusters=4)

        st.session_state.cluster_labels    = list(labels)
        st.session_state.kmeans            = kmeans
        st.session_state.chunk_cluster_map = {i: int(l) for i, l in enumerate(labels)}

        topic_names = {}
        for cluster_id in set(labels):
            cluster_chunks_list = [chunks[i] for i in range(len(chunks)) if labels[i] == cluster_id]
            time.sleep(2)
            topic_names[cluster_id] = generate_topic_name(cluster_chunks_list)

        st.session_state.topic_names        = topic_names
        st.session_state.total_chunks_stored += len(chunks)

        st.session_state.doc_embeddings[source_name]   = embeddings.mean(axis=0)
        st.session_state.doc_chunk_counts[source_name] = len(chunks)

        topic_dist = {}
        for i, label in enumerate(labels):
            tname = topic_names.get(int(label), f"Cluster {label}")
            topic_dist[tname] = topic_dist.get(tname, 0) + 1
        st.session_state.doc_topic_maps[source_name] = topic_dist

        store_chunks(chunks, embeddings, source_name, labels)
        st.session_state.document_names.add(source_name)
        st.session_state.processed_files.add(source_name)

        is_url = source_name.startswith("http") or "(" in source_name
        label  = f"web page ({source_name})" if is_url else f"PDF ({source_name})"
        new_suggestions = generate_suggestions(chunks, n=8, source_label=label)
        existing = set(st.session_state.pdf_suggestions)
        for s in new_suggestions:
            if s not in existing:
                st.session_state.pdf_suggestions.append(s)
                existing.add(s)
        st.session_state.pdf_suggestions = st.session_state.pdf_suggestions[-20:]

        st.session_state.doc_summaries[source_name] = summarize_document(chunks, source_label=label)

        return chunks, topic_names

    tab_pdf, tab_url = st.tabs(["📄  PDF Upload", "🌐  From URL"])

    with tab_pdf:
        uploaded_files = st.file_uploader(
            "Drop PDFs here or click to browse",
            type=["pdf"], accept_multiple_files=True,
            label_visibility="visible"
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
                    chunks, topic_names = _index_text(text, uploaded_file.name)

                st.success(f"✅ **{uploaded_file.name}** indexed — {len(chunks)} chunks · {len(topic_names)} topics")

                if topic_names:
                    pills = " ".join([f'<span class="cb-pill">{n}</span>' for n in topic_names.values()])
                    st.markdown(f'<div style="margin:4px 0 16px"><div class="cb-pill-row">{pills}</div></div>', unsafe_allow_html=True)

                with st.expander("📝 Document summary"):
                    st.markdown(st.session_state.doc_summaries.get(uploaded_file.name, "Summary unavailable."))
                
    with tab_url:
        st.markdown("""
        <div class="cb-url-box">
          <div class="cb-url-box-title">🌐 Index a web page or online PDF</div>
          <div class="cb-url-box-sub">
            Paste any public URL — a web article, documentation page, blog post,
            or a direct link to a PDF. Company Brain will fetch and index it just like an uploaded file.
          </div>
          <div class="cb-url-examples">
            Works with:
            <span>https://docs.example.com/guide</span> &nbsp;·&nbsp;
            <span>https://arxiv.org/pdf/2301.00001.pdf</span> &nbsp;·&nbsp;
            <span>https://en.wikipedia.org/wiki/Topic</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        url_input = st.text_area(
            "Enter one or more URLs (one per line)",
            placeholder="https://example.com/document\nhttps://arxiv.org/pdf/paper.pdf",
            height=80,
            label_visibility="collapsed",
        )

        uc1, uc2, uc3 = st.columns([2, 2, 3])
        with uc1:
            max_depth = st.selectbox("Crawl depth", options=[1, 2, 3], index=1,
                                     help="1 = single page only · 2 = page + linked subpages · 3 = deeper crawl")
        with uc2:
            max_pages = st.selectbox("Max pages", options=[1, 5, 10, 20, 30], index=2,
                                     help="Max number of pages to fetch per URL")

        col_btn, _ = st.columns([1, 5])
        with col_btn:
            fetch_clicked = st.button("🌐 Fetch & Index", type="primary", use_container_width=True, key="fetch_url_btn")

        if fetch_clicked and url_input.strip():
            urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()]

            for url in urls:
                if url in st.session_state.processed_files:
                    st.markdown(f"""
                    <div class="cb-file-item">
                      <div class="cb-file-icon">🌐</div>
                      <div class="cb-file-info">
                        <div class="cb-file-name">{url[:70]}{'…' if len(url)>70 else ''}</div>
                        <div class="cb-file-sub">Already indexed — no re-processing needed</div>
                        <div class="cb-prog-bg"><div class="cb-prog" style="width:100%;background:#4CAF7D"></div></div>
                      </div>
                      <span class="cb-status status-indexed">Indexed</span>
                    </div>
                    """, unsafe_allow_html=True)
                    continue

                st.markdown(f"""
                <div class="cb-file-item">
                  <div class="cb-file-icon">🌐</div>
                  <div class="cb-file-info">
                    <div class="cb-file-name">{url[:70]}{'…' if len(url)>70 else ''}</div>
                    <div class="cb-file-sub">Fetching page and extracting text...</div>
                    <div class="cb-prog-bg"><div class="cb-prog" style="width:40%;background:#8B7FF0"></div></div>
                  </div>
                  <span class="cb-status status-indexing">Fetching</span>
                </div>
                """, unsafe_allow_html=True)

                try:
                    with st.spinner(f"Fetching {url[:60]}..."):
                        text, source_name = extract_text_from_url(url, max_depth=max_depth, max_pages=max_pages)

                    st.markdown(f"""
                    <div class="cb-file-item">
                      <div class="cb-file-icon">🌐</div>
                      <div class="cb-file-info">
                        <div class="cb-file-name">{source_name}</div>
                        <div class="cb-file-sub">Indexing — chunking, embedding, clustering...</div>
                        <div class="cb-prog-bg"><div class="cb-prog" style="width:70%;background:#8B7FF0"></div></div>
                      </div>
                      <span class="cb-status status-indexing">Indexing</span>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.spinner(f"Indexing {source_name}..."):
                        chunks, topic_names = _index_text(text, source_name)

                    st.session_state.processed_files.add(url)
                    st.success(f"✅ **{source_name}** indexed — {len(chunks)} chunks · {len(topic_names)} topics · {max_pages} page(s) crawled")

                    if topic_names:
                        pills = " ".join([f'<span class="cb-pill">{n}</span>' for n in topic_names.values()])
                        st.markdown(f'<div style="margin:4px 0 16px"><div class="cb-pill-row">{pills}</div></div>', unsafe_allow_html=True)

                    with st.expander("📝 Document summary"):
                        st.markdown(st.session_state.doc_summaries.get(source_name, "Summary unavailable."))

                except ValueError as e:
                    st.error(f"❌ **{url[:60]}** — {e}")
                except Exception as e:
                    st.error(f"❌ Unexpected error for **{url[:60]}**: {e}")

        elif fetch_clicked:
            st.warning("Please enter at least one URL.")

    if st.session_state.document_names:
        st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
        st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">📁 Indexed sources</span></div>', unsafe_allow_html=True)
        colors_bg = ["#2a2560","#0d1e35","#0d2e1a","#2e1e0d","#0d2e28"]
        for i, doc in enumerate(list(st.session_state.document_names)):
            bg     = colors_bg[i % len(colors_bg)]
            ico    = "🌐" if doc.startswith("http") else "📄"
            chunks = st.session_state.doc_chunk_counts.get(doc, "?")
            topics = len(st.session_state.doc_topic_maps.get(doc, {}))
            st.markdown(f"""
            <div class="cb-file-item">
              <div class="cb-file-icon" style="background:{bg}">{ico}</div>
              <div class="cb-file-info">
                <div class="cb-file-name">{doc}</div>
                <div class="cb-file-sub">{chunks} chunks · {topics} topics · Chunked · Embedded · Clustered</div>
                <div class="cb-prog-bg"><div class="cb-prog" style="width:100%;background:#4CAF7D"></div></div>
              </div>
              <span class="cb-status status-indexed">Indexed</span>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📝 Summary — {doc}"):
                st.markdown(st.session_state.doc_summaries.get(doc, "No summary available."))

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
                Consider uploading more relevant documents to fill these gaps.
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">Unanswered questions</span></div>', unsafe_allow_html=True)
            for gq in st.session_state.knowledge_gaps:
                st.markdown(f"""
                <div class="cb-query-item" style="border-color:#3a2e10">
                  <span style="font-size:18px">⚠️</span>
                  <div style="flex:1">
                    <div class="cb-query-q" style="color:#a08040">{gq}</div>
                    <div class="cb-query-meta" style="color:#5a4020">Low confidence · No matching document found</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑️ Clear knowledge gaps", type="secondary", key="clear_gaps_btn"):
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
            <div style="margin-bottom:8px">🔍 <strong style="color:#aaa">Check document quality</strong><br>Make sure uploaded PDFs have readable, searchable text.</div>
            <div>🔢 <strong style="color:#aaa">Increase clusters</strong><br>If your documents cover many topics, increase the cluster count for better retrieval.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.query_history:
            st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
            st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">📊 Confidence distribution</span></div>', unsafe_allow_html=True)
            scores = [q["score"] for q in st.session_state.query_history]
            fig, ax = plt.subplots(figsize=(4, 2), facecolor="#13131a")
            ax.hist(scores, bins=10, color="#6B5CE7", edgecolor="#0e0e11", range=(0,1))
            ax.set_facecolor("#13131a")
            ax.tick_params(colors="#555", labelsize=8)
            ax.spines[:].set_color("#1E1E5E")
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
      <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>RAG · Hybrid Retrieval · Groq Dual-Model · LLM-as-Judge</div>
      <h1>How <span>Company Brain</span> works</h1>
      <p>A full Retrieval-Augmented Generation (RAG) pipeline — from raw PDF or URL to intelligent, context-aware, self-scored answers. Built with sentence-transformers, ChromaDB, K-Means clustering, and Groq.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🚀 Core features</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-features">
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#1e1a35">🔢</div><h3>Semantic Vector Search</h3><p>Documents are embedded using <strong style="color:#aaa">all-MiniLM-L6-v2</strong> into 384-dimensional vectors and stored in ChromaDB, matched by similarity — finding meaning, not just keywords.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#0d1e35">🏷️</div><h3>Auto Topic Clustering</h3><p><strong style="color:#aaa">K-Means clustering</strong> groups document chunks into topics automatically. Groq names each cluster in plain language (2–4 words) — no manual tagging needed.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#0d2e1a">🔍</div><h3>Hybrid Retrieval</h3><p>Every query is routed to its predicted topic cluster for <strong style="color:#aaa">cluster-scoped vector search</strong>, then merged with a <strong style="color:#aaa">keyword search</strong> pass across all chunks for extra recall.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#2e1e0d">💬</div><h3>Conversation Memory</h3><p>Company Brain keeps a rolling window of the last <strong style="color:#aaa">4 messages</strong> and feeds it back into every prompt, enabling natural follow-up questions.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#0d2e28">⚡</div><h3>LLM-as-Judge Scoring</h3><p>A second Groq model scores every answer for <strong style="color:#aaa">faithfulness</strong> and <strong style="color:#aaa">relevancy</strong> (0–1 each). If either falls below 0.5, the answer is regenerated — up to <strong style="color:#aaa">3 attempts</strong>.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#2a1030">💡</div><h3>Smart Suggestions</h3><p>After indexing, Groq samples chunks and generates <strong style="color:#aaa">specific, answerable questions</strong> shown as chips on the Ask AI page, plus contextual follow-ups after every answer.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#1a2a3a">🌐</div><h3>URL &amp; Web Crawling</h3><p>Paste a link instead of a file. Direct PDF URLs are parsed in place; regular web pages are crawled recursively (configurable depth &amp; page limit) and cleaned with BeautifulSoup.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#3a1a2a">⚠️</div><h3>Knowledge Gap Detection</h3><p>Any answer scoring below <strong style="color:#aaa">40% confidence</strong> is logged as a knowledge gap — a visible signal of what your document set is still missing.</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🛠️ Tech stack</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-features" style="grid-template-columns:repeat(4,1fr)">
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#1e1a35;font-size:22px">🤗</div><h3>Sentence Transformers</h3><p><code style="color:#a78bfa;font-size:10px">all-MiniLM-L6-v2</code><br>Creates dense semantic embeddings from text chunks.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#0d1e35;font-size:22px">🗄️</div><h3>ChromaDB</h3><p>Persistent vector store. Cluster-filtered queries (<code style="color:#5BA4E5;font-size:10px">where: cluster</code>) keep retrieval scoped to the right topic.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#0d2e1a;font-size:22px">⚡</div><h3>Groq — Dual Model</h3><p><code style="color:#4CAF7D;font-size:10px">llama-3.3-70b-versatile</code> generates answers, names topics &amp; writes suggestions. <code style="color:#4CAF7D;font-size:10px">llama-3.1-8b-instant</code> judges each answer.</p></div>
      <div class="cb-feature"><div class="cb-feature-icon" style="background:#2e1e0d;font-size:22px">📐</div><h3>LangChain</h3><p><code style="color:#E5945B;font-size:10px">RecursiveCharacterTextSplitter</code> (1,000 / 200 overlap) for chunking, <code style="color:#E5945B;font-size:10px">RecursiveUrlLoader</code> for multi-page web crawling.</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="cb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="cb-sec-hdr"><span class="cb-sec-title">🔄 RAG pipeline</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cb-pipeline-wrap">
      <div class="cb-pipeline">
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">📄</div><div class="cb-pipeline-label">PDF / URL</div><div class="cb-pipeline-sub">PyPDF or web crawl</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">✂️</div><div class="cb-pipeline-label">Chunking</div><div class="cb-pipeline-sub">1000 chars / 200 overlap</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">🔢</div><div class="cb-pipeline-label">Embedding</div><div class="cb-pipeline-sub">384-dim vectors</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">🏷️</div><div class="cb-pipeline-label">Clustering</div><div class="cb-pipeline-sub">K-Means + Groq naming</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">🗄️</div><div class="cb-pipeline-label">ChromaDB</div><div class="cb-pipeline-sub">Persistent storage</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">🔍</div><div class="cb-pipeline-label">Hybrid Retrieval</div><div class="cb-pipeline-sub">Cluster vector + keyword</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">⚡</div><div class="cb-pipeline-label">Groq Answer</div><div class="cb-pipeline-sub">+ chat history</div></div>
        <div class="cb-pipeline-arrow">→</div>
        <div class="cb-pipeline-step"><div class="cb-pipeline-icon">⚖️</div><div class="cb-pipeline-label">Judge &amp; Retry</div><div class="cb-pipeline-sub">Faithfulness + relevancy</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)               