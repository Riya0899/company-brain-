# frontend/app.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import styles
from views import dashboard, chat, upload, gaps, features

st.set_page_config(page_title="Company Brain", layout="wide", page_icon="🧠")
styles.inject()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

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

    nav_items = [
        ("dashboard", "📊 Dashboard"),
        ("chat", "✨ Ask AI"),
        ("upload", "📤 Upload"),
        ("gaps", "⚠️ Gaps"),
        ("features", "⚡ Features"),
    ]
    for key, label in nav_items:
        is_active = st.session_state.page == key
        if st.button(label, use_container_width=True, key=f"nav_{key}",
                     type="primary" if is_active else "secondary"):
            st.session_state.page = key
            st.rerun()

page = st.session_state.page
if page == "dashboard":
    dashboard.render()
elif page == "chat":
    chat.render()
elif page == "upload":
    upload.render()
elif page == "gaps":
    gaps.render()
elif page == "features":
    features.render()