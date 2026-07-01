# frontend/views/gaps.py
import streamlit as st
import matplotlib.pyplot as plt
import api_client as api

def render():
    st.markdown('<div class="cb-content">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:18px;font-weight:700;color:#fff">⚠️ Knowledge Gaps</div>', unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="medium")

    with left:
        gaps = api.get_gaps()
        if not gaps:
            st.success("No knowledge gaps yet.")
        for g in gaps:
            st.markdown(f"""
            <div class="cb-gap"><span>⚠️</span><div class="cb-gap-text">{g['question']}</div></div>
            """, unsafe_allow_html=True)

    with right:
        history = api.get_history()
        if history:
            st.markdown('<div style="font-size:13px;color:#bbb;font-weight:600;margin-bottom:10px">📊 Confidence distribution</div>', unsafe_allow_html=True)
            scores = [h["score"] for h in history if h["score"] is not None]
            fig, ax = plt.subplots(figsize=(4, 2.5), facecolor="#13131a")
            ax.hist(scores, bins=10, color="#6B5CE7", edgecolor="#0e0e11", range=(0, 1))
            ax.set_facecolor("#13131a")
            ax.tick_params(colors="#555", labelsize=8)
            ax.spines[:].set_color("#232330")
            ax.set_xlabel("Confidence score", color="#555", fontsize=8)
            ax.set_ylabel("# queries", color="#555", fontsize=8)
            st.pyplot(fig)
            plt.close()
        else:
            st.markdown('<div style="color:#444;font-size:12px;text-align:center;padding:20px 0">Ask some questions to see this chart.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)