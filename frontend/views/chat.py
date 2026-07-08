import streamlit as st
import requests
import api_client as api

def confidence_bar(score: float) -> str:
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

def render_sources(sources):
    if not sources:
        return
    with st.expander(f"📚 Sources ({len(sources)})"):
        for s in sources:
            st.markdown(f"""
            <div style="background:#13131a;border:0.5px solid #232330;border-radius:8px;
                        padding:10px 14px;margin-bottom:6px;">
              <div style="font-size:11px;color:#a78bfa;font-weight:600;margin-bottom:4px;">📄 {s['source']}</div>
              <div style="font-size:12px;color:#888;">{s['snippet']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_chips(questions, key_prefix):
    clicked = None
    cols = st.columns(len(questions))
    for i, q in enumerate(questions):
        with cols[i]:
            if st.button(f"💬 {q}", key=f"{key_prefix}_{i}", use_container_width=True):
                clicked = q
    return clicked

def show_thinking():
    placeholder = st.empty()
    placeholder.markdown("""
    <div style="display:flex;gap:4px;align-items:center;padding:6px 0">
      <span style="width:6px;height:6px;border-radius:50%;background:#8B7FF0"></span>
      <span style="font-size:12px;color:#666;margin-left:6px">Thinking...</span>
    </div>
    """, unsafe_allow_html=True)
    return placeholder

def render():
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:16px">
      <div style="font-size:18px;font-weight:700;color:#fff">✨ Ask AI</div>
      <div style="font-size:12px;color:#555;margin-top:3px">Ask anything about your uploaded documents.</div>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chip_query = st.session_state.pop("_chip_query", None)

    # ── Welcome screen + suggested questions (only when chat is empty) ──
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:36px 0">
          <div style="font-size:44px;margin-bottom:12px">🧠</div>
          <div style="font-size:18px;color:#fff;font-weight:700;margin-bottom:4px">What would you like to know?</div>
          <div style="font-size:12px;color:#555">Pick a suggestion below or type your own question.</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            suggestions = api.get_suggestions()
        except Exception as e:
            suggestions = []
            st.warning(f"Couldn't load suggestions: {e}")

        if suggestions:
            st.markdown('<div style="font-size:11px;color:#555;text-transform:uppercase;margin-bottom:10px">Suggested from your documents</div>', unsafe_allow_html=True)
            clicked = render_chips(suggestions[:4], "suggest")
            if clicked:
                chip_query = clicked

    # ── Render chat history ──
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🧠" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
            if m["role"] == "assistant" and "score" in m:
                st.markdown(confidence_bar(m["score"]), unsafe_allow_html=True)
                render_sources(m.get("sources", []))

    # ── Follow-up chips after the last assistant message ──
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        followups = st.session_state.messages[-1].get("followups", [])
        if followups and not chip_query:
            st.markdown('<div style="font-size:11px;color:#555;text-transform:uppercase;margin:12px 0 8px">💡 Follow-up suggestions</div>', unsafe_allow_html=True)
            clicked = render_chips(followups, "followup")
            if clicked:
                chip_query = clicked

    query = st.chat_input("Ask a question about your documents...")
    if chip_query:
        query = chip_query

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        thinking = show_thinking()
        try:
            result = api.chat(query, st.session_state.messages)
        except Exception as e:
            thinking.empty()
            st.error(f"❌ {e}")
            st.stop()
        thinking.empty()

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(result["answer"])
            st.markdown(confidence_bar(result["score"]), unsafe_allow_html=True)
            render_sources(result.get("sources", []))

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "score": result["score"],
            "sources": result.get("sources", []),
            "followups": [],
        })

        try:
            resp = requests.post(f"{api.BASE}/followups", json={
                "question": query,
                "answer": result["answer"],
                "topic": result.get("topic", ""),
            })
            if resp.ok:
                st.session_state.messages[-1]["followups"] = resp.json().get("followups", [])
            else:
                st.session_state.messages[-1]["followups"] = []
        except Exception:
            st.session_state.messages[-1]["followups"] = []

        st.rerun()

    if st.session_state.messages:
        if st.button("🧹 Clear chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)