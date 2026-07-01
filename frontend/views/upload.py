# frontend/views/upload.py
import streamlit as st
import api_client as api

def render():
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-hero" style="padding:28px 32px;margin-bottom:20px">
      <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>PDF · URL · Web crawl</div>
      <h1 style="font-size:24px">Feed the <span>Brain</span></h1>
      <p>Upload a PDF or paste a link — Company Brain extracts, chunks, embeds, and clusters it automatically.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-stats" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px">
      <div class="cb-stat"><div style="font-size:20px">📄</div><div class="cb-stat-label" style="margin-top:6px">Extract text</div></div>
      <div class="cb-stat"><div style="font-size:20px">✂️</div><div class="cb-stat-label" style="margin-top:6px">Chunk (1000/200)</div></div>
      <div class="cb-stat"><div style="font-size:20px">🔢</div><div class="cb-stat-label" style="margin-top:6px">Embed (384-dim)</div></div>
      <div class="cb-stat"><div style="font-size:20px">🏔️</div><div class="cb-stat-label" style="margin-top:6px">Cluster (HDBSCAN)</div></div>
    </div>
    """, unsafe_allow_html=True)

    tab_pdf, tab_url = st.tabs(["📄 Upload PDF", "🌐 From URL"])

    with tab_pdf:
        file = st.file_uploader("Drop a PDF here", type=["pdf"], label_visibility="collapsed")
        if file:
            st.markdown(f"""
            <div class="cb-doc"><div class="cb-doc-icon">📄</div>
              <div><div class="cb-doc-name">{file.name}</div><div class="cb-doc-meta">Ready to index</div></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚡ Index this PDF", type="primary", key="idx_pdf"):
                with st.spinner(f"Indexing {file.name}..."):
                    result = api.upload_pdf(file)
                st.success(f"✅ **{result['filename']}** indexed — {result['chunks']} chunks · {len(result['topics'])} topics")
                if result["topics"]:
                    pills = "".join(f'<span class="cb-pill">{n}</span>' for n in result["topics"].values())
                    st.markdown(pills, unsafe_allow_html=True)
                with st.expander("📝 Document summary"):
                    st.markdown(result["summary"])

    with tab_url:
        st.markdown("""
        <div style="font-size:12px;color:#666;margin-bottom:12px;line-height:1.6">
          Paste a public URL — an article, docs page, or direct PDF link.
        </div>
        """, unsafe_allow_html=True)
        url = st.text_input("URL", placeholder="https://example.com/article", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            max_depth = st.selectbox("Crawl depth", [1, 2, 3], index=1)
        with c2:
            max_pages = st.selectbox("Max pages", [1, 5, 10, 20], index=2)

        if st.button("🌐 Fetch & Index", type="primary", key="idx_url") and url.strip():
            with st.spinner(f"Fetching {url[:50]}..."):
                try:
                    result = api.upload_url(url, max_depth, max_pages)
                    st.success(f"✅ **{result['filename']}** indexed — {result['chunks']} chunks · {len(result['topics'])} topics")
                    if result["topics"]:
                        pills = "".join(f'<span class="cb-pill">{n}</span>' for n in result["topics"].values())
                        st.markdown(pills, unsafe_allow_html=True)
                    with st.expander("📝 Document summary"):
                        st.markdown(result["summary"])
                except Exception as e:
                    st.error(f"❌ Failed to index URL: {e}")

    st.markdown('<hr style="border-color:#1e1e2a;margin:28px 0">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:#bbb;font-weight:600;margin-bottom:12px">📁 Indexed sources</div>', unsafe_allow_html=True)

    docs = api.get_documents()
    if not docs:
        st.markdown("""
        <div class="cb-empty">
          <div class="cb-empty-icon">📭</div>
          <div style="font-size:14px;color:#666;font-weight:600;margin-bottom:4px">No documents yet</div>
          <div style="font-size:12px">Upload a PDF or paste a URL above to build your knowledge base.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for d in docs:
            icon = "🌐" if d["source_name"].startswith("http") or "(" in d["source_name"] else "📄"
            st.markdown(f"""
            <div class="cb-doc">
              <div class="cb-doc-icon">{icon}</div>
              <div style="flex:1"><div class="cb-doc-name">{d['source_name']}</div>
              <div class="cb-doc-meta">{d['chunk_count']} chunks · indexed</div></div>
              <span style="color:#4CAF7D;font-size:12px">✓</span>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📝 Summary"):
                st.markdown(d.get("summary", "No summary available."))

    st.markdown('</div>', unsafe_allow_html=True)