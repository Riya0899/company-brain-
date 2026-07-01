# frontend/styles.py
import streamlit as st

def inject():
    st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}

header[data-testid="stHeader"] {
    visibility: visible !important;
    background: transparent !important;
    height: auto !important;
}

header[data-testid="stHeader"] [data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    color: #ccc !important;
    z-index: 999999 !important;
    position: relative !important;
}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    body, .stApp { background: #0e0e11 !important; color: #ccc; font-family: -apple-system, sans-serif; }
    section[data-testid="stSidebar"] { background: #13131a !important; border-right: 0.5px solid #232330 !important; }
    .cb-content { padding: 24px 28px; animation: fadeIn .35s ease; }

    @keyframes fadeIn { from {opacity:0; transform:translateY(6px);} to {opacity:1; transform:translateY(0);} }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
    @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
    @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-5px)} }
    @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

    /* ── Hero ─────────────────────────────────────────── */
    .cb-hero {
        background: linear-gradient(135deg, #13131a 0%, #1a1630 50%, #13131a 100%);
        background-size: 200% 200%;
        animation: shimmer 8s ease infinite;
        border: 0.5px solid #2e2e42; border-radius: 16px;
        padding: 36px 40px; margin-bottom: 24px; position: relative; overflow: hidden;
    }
    .cb-hero::before {
        content:''; position:absolute; top:-60px; right:-40px; width:300px; height:300px;
        background: radial-gradient(circle, #6B5CE733 0%, transparent 70%); pointer-events:none;
        animation: float 6s ease-in-out infinite;
    }
    .cb-hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: #1e1a35; border: 0.5px solid #6B5CE744; border-radius: 20px;
        padding: 5px 13px; font-size: 11px; color: #a78bfa; margin-bottom: 14px;
    }
    .cb-hero-badge-dot { width:6px; height:6px; border-radius:50%; background:#6B5CE7; display:inline-block; animation: pulse 1.5s infinite; }
    .cb-hero h1 { font-size: 30px; font-weight: 700; color: #fff; margin: 0 0 10px; letter-spacing: -0.8px; }
    .cb-hero h1 span { background: linear-gradient(90deg, #a78bfa, #60a5fa, #a78bfa); background-size:200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 4s linear infinite; }
    .cb-hero p { font-size: 14px; color: #777; line-height: 1.7; max-width: 560px; margin: 0; }

    /* ── Stat cards ───────────────────────────────────── */
    .cb-stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px; }
    .cb-stat {
        background: #13131a; border: 0.5px solid #232330; border-radius: 14px; padding: 18px 20px;
        transition: all .25s ease; cursor: default;
    }
    .cb-stat:hover { border-color: #6B5CE788; transform: translateY(-3px); box-shadow: 0 8px 24px #00000055; }
    .cb-stat-num { font-size: 32px; font-weight: 700; margin-bottom: 4px; letter-spacing: -1px; }
    .cb-stat-label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }

    /* ── Doc / query cards ────────────────────────────── */
    .cb-doc {
        background: #13131a; border: 0.5px solid #232330; border-radius: 12px;
        padding: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px;
        transition: all .2s ease;
    }
    .cb-doc:hover { border-color: #3a3a55; background:#16161f; transform: translateX(2px); }
    .cb-doc-icon {
        width: 38px; height: 38px; border-radius: 10px;
        background: linear-gradient(135deg,#2a2560,#1e1a35);
        display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink:0;
    }
    .cb-doc-name { font-size: 13px; color: #ccc; font-weight: 500; margin-bottom: 4px; }
    .cb-doc-meta { font-size: 11px; color: #555; }

    /* ── Gap / empty states ───────────────────────────── */
    .cb-gap {
        background: #1a150d; border: 0.5px solid #3a2e10; border-radius: 12px;
        padding: 14px 18px; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px;
        transition: border-color .2s;
    }
    .cb-gap:hover { border-color: #d4a84066; }
    .cb-gap-text { font-size: 12px; color: #a08040; line-height: 1.6; }

    .cb-empty {
        text-align:center; padding:44px 20px; color:#444;
        background:#0f0f14; border:1px dashed #232330; border-radius:14px;
    }
    .cb-empty-icon { font-size:34px; margin-bottom:10px; animation: float 3s ease-in-out infinite; }

    /* ── Pills ────────────────────────────────────────── */
    .cb-pill {
        font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;
        background: #1e1a35; border: 0.5px solid #6B5CE744; color: #a78bfa; margin-right: 6px;
        display:inline-block; margin-bottom:6px; transition: all .15s;
    }
    .cb-pill:hover { border-color:#6B5CE7; background:#241e45; transform: translateY(-1px); }

    /* ── Sidebar ──────────────────────────────────────── */
    .cb-sidebar-logo {
        display:flex; align-items:center; gap:10px; padding:0 4px 18px; margin-bottom:6px;
        border-bottom:0.5px solid #232330;
    }
    .cb-logo-icon {
        width:36px; height:36px; border-radius:10px; font-size:18px;
        background: linear-gradient(135deg,#6B5CE7,#a78bfa);
        display:flex; align-items:center; justify-content:center;
        box-shadow: 0 0 18px #6B5CE744;
    }
    .cb-logo-text { color:#fff; font-size:15px; font-weight:700; letter-spacing:-0.3px; }
    .cb-logo-sub { font-size:10px; color:#555; }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background: transparent !important; border: 0.5px solid transparent !important;
        color: #888 !important; font-size: 13px !important; font-weight: 500 !important;
        justify-content: flex-start !important; padding: 10px 14px !important;
        border-radius: 9px !important; box-shadow: none !important; transition: all .15s !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: #1a1a24 !important; color: #ddd !important; border-color: #2e2e42 !important;
        transform: translateX(2px);
    }

    /* ── General buttons ──────────────────────────────── */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg,#6B5CE7,#8b5cf6) !important; color:#fff !important;
        border: none !important; box-shadow: 0 4px 16px #6B5CE744 !important;
        transition: all .2s ease !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 6px 22px #6B5CE766 !important;
    }

    /* ── Chat ─────────────────────────────────────────── */
    .stChatMessage {
        background: #13131a !important; border: 0.5px solid #232330 !important;
        border-radius: 14px !important; animation: fadeIn .3s ease;
    }
    .stChatInput > div { background: #1a1a24 !important; border: 0.5px solid #2e2e42 !important; border-radius: 12px !important; }
    .stChatInput textarea { color: #ccc !important; background: transparent !important; }

    .cb-thinking { display:flex; gap:4px; align-items:center; padding:6px 0; }
    .cb-thinking span {
        width:6px; height:6px; border-radius:50%; background:#8B7FF0;
        animation: bounce 1.2s infinite ease-in-out;
    }
    .cb-thinking span:nth-child(2){animation-delay:.15s}
    .cb-thinking span:nth-child(3){animation-delay:.3s}

    /* ── Uploader ─────────────────────────────────────── */
    div[data-testid="stFileUploadDropzone"] {
        background: #16161f !important; border: 1.5px dashed #2e2e42 !important; border-radius: 14px !important;
        transition: border-color .2s;
    }
    div[data-testid="stFileUploadDropzone"]:hover { border-color: #6B5CE7 !important; }

    /* ── Misc ─────────────────────────────────────────── */
    .stProgress > div > div { background: linear-gradient(90deg, #6B5CE7, #a78bfa) !important; }
    .stExpander { background: #13131a !important; border: 0.5px solid #232330 !important; border-radius: 10px !important; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)