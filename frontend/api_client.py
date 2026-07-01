# frontend/api_client.py
import requests

BASE = "http://localhost:8000"

def upload_pdf(file):
    return requests.post(f"{BASE}/upload", files={"file": file}).json()

def upload_url(url, max_depth=2, max_pages=10):
    return requests.post(f"{BASE}/upload-url", json={
        "url": url, "max_depth": max_depth, "max_pages": max_pages
    }).json()

def chat(query, messages):
    return requests.post(f"{BASE}/chat", json={"query": query, "messages": messages}).json()

def get_documents():
    return requests.get(f"{BASE}/documents").json()

def get_topics():
    return requests.get(f"{BASE}/topics").json()

def get_gaps():
    return requests.get(f"{BASE}/gaps").json()

def get_history():
    return requests.get(f"{BASE}/history").json()

def get_stats():
    return requests.get(f"{BASE}/stats").json()

def get_suggestions():
    return requests.get(f"{BASE}/suggestions").json()