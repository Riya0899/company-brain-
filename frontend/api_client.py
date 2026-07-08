import requests
import streamlit as st

BASE = "http://localhost:8000"

def _post(path, **kwargs):
    resp = requests.post(f"{BASE}{path}", **kwargs)
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        st.error(f"Backend error ({resp.status_code}): {detail}")
        st.stop()
    return resp.json()

def _get(path, **kwargs):
    resp = requests.get(f"{BASE}{path}", **kwargs)
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        st.error(f"Backend error ({resp.status_code}): {detail}")
        st.stop()
    return resp.json()

def upload_pdf(file):
    return _post("/upload", files={"file": file})

def upload_url(url, max_depth=2, max_pages=10):
    return _post("/upload-url", json={"url": url, "max_depth": max_depth, "max_pages": max_pages})

def chat(query, messages):
    return _post("/chat", json={"query": query, "messages": messages})

def get_followups(question, answer, topic=""):
    return _post("/followups", json={"question": question, "answer": answer, "topic": topic})

def get_documents():
    return _get("/documents")

def get_topics():
    return _get("/topics")

def get_gaps():
    return _get("/gaps")

def get_history():
    return _get("/history")

def get_stats():
    return _get("/stats")

def get_suggestions():
    return _get("/suggestions")