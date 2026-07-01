# frontend/views/dashboard.py
import streamlit as st
import matplotlib.pyplot as plt
import api_client as api

def render():
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    docs = api.get_documents()
    topics = api.get_topics()
    stats = api.get_stats()
    history = api.get_history()

    doc_count = len(docs)
    st.markdown(f"""
    <div class="cb-hero">
      <div class="cb-hero-badge"><span class="cb-hero-badge-dot"></span>Knowledge base active · {doc_count} document{'s' if doc_count != 1 else ''}</div>
      <h1>Ask anything about<br><span>your company docs.</span></h1>
      <p>{len(topics)} topics discovered · {stats['total_queries']} question{'s' if stats['total_queries'] != 1 else ''} answered so far.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cb-stats" style="grid-template-columns:repeat(5,1fr)">
      <div class="cb-stat"><div class="cb-stat-num" style="color:#a78bfa">{doc_count}</div><div class="cb-stat-label">Documents</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#5BA4E5">{len(topics)}</div><div class="cb-stat-label">Topics</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#60a5fa">{int(stats['avg_score']*100)}%</div><div class="cb-stat-label">Avg. confidence</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#4CAF7D">{int(stats['avg_faithfulness']*100)}%</div><div class="cb-stat-label">Avg. faithfulness</div></div>
      <div class="cb-stat"><div class="cb-stat-num" style="color:#E5945B">{int(stats['avg_relevancy']*100)}%</div><div class="cb-stat-label">Avg. relevancy</div></div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="medium")

    with left:
        if topics:
            st.markdown('<div style="font-size:14px;color:#bbb;font-weight:600;margin-bottom:12px">🏷️ Topic distribution</div>', unsafe_allow_html=True)
            counts = list(topics.keys())
            labels = list(topics.values())
            colors = ["#8B7FF0", "#4CAF7D", "#E5945B", "#5BA4E5", "#E57FAA", "#4ECBA5"]
            fig, ax = plt.subplots(figsize=(5, 3), facecolor="#13131a")
            ax.pie([1]*len(labels), labels=labels, autopct=lambda p: f"{p:.0f}%" if p > 5 else "",
                   colors=colors[:len(labels)], textprops={"color": "#aaa", "fontsize": 9},
                   wedgeprops={"linewidth": 1.5, "edgecolor": "#0e0e11"})
            ax.set_facecolor("#13131a")
            st.pyplot(fig)
            plt.close()
            pills = "".join(f'<span class="cb-pill">{n}</span>' for n in topics.values())
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="cb-empty">
              <div class="cb-empty-icon">🏷️</div>
              <div style="font-size:14px;color:#666;font-weight:600">No topics yet</div>
              <div style="font-size:12px">Upload documents to see topic clusters here.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color:#1e1e2a;margin:20px 0">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;color:#bbb;font-weight:600;margin-bottom:12px">📁 Indexed documents</div>', unsafe_allow_html=True)
        if not docs:
            st.markdown("""
            <div class="cb-empty">
              <div class="cb-empty-icon">📭</div>
              <div style="font-size:14px;color:#666;font-weight:600">No documents yet</div>
              <div style="font-size:12px">Head to Upload to add your first PDF.</div>
            </div>
            """, unsafe_allow_html=True)
        for d in docs:
            st.markdown(f"""
            <div class="cb-doc">
              <div class="cb-doc-icon">📄</div>
              <div style="flex:1"><div class="cb-doc-name">{d['source_name']}</div>
              <div class="cb-doc-meta">{d['chunk_count']} chunks · indexed</div></div>
              <span style="color:#4CAF7D;font-size:12px">✓</span>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div style="font-size:14px;color:#bbb;font-weight:600;margin-bottom:12px">🕑 Recent queries</div>', unsafe_allow_html=True)
        if not history:
            st.markdown("""
            <div class="cb-empty">
              <div class="cb-empty-icon">💬</div>
              <div style="font-size:14px;color:#666;font-weight:600">No queries yet</div>
              <div style="font-size:12px">Ask a question in the Ask AI tab.</div>
            </div>
            """, unsafe_allow_html=True)
        for h in history[:10]:
            score = h["score"] or 0
            color = "#4CAF7D" if score >= 0.7 else ("#E5945B" if score >= 0.4 else "#E57070")
            st.markdown(f"""
            <div class="cb-doc" style="align-items:flex-start">
              <div style="flex:1">
                <div class="cb-doc-name">💬 {h['question'][:55]}{'…' if len(h['question'])>55 else ''}</div>
                <div class="cb-doc-meta">🏷️ {h['topic'] or '—'} &nbsp;·&nbsp; F:{int((h['faithfulness'] or 0)*100)}% R:{int((h['relevancy'] or 0)*100)}%</div>
              </div>
              <span style="font-size:11px;font-weight:600;color:{color}">{int(score*100)}%</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)