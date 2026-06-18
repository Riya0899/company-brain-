"""
url_reader.py
-------------
Fetches a URL and extracts clean readable text from it.
Uses LangChain RecursiveUrlLoader for deep multi-page crawling.
Falls back to single-page requests for direct PDF links.
"""

import re
import requests
from io import BytesIO
from pypdf import PdfReader
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15


def _bs4_extractor(html: str) -> str:
    """Clean extractor passed to RecursiveUrlLoader."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer",
                     "header", "aside", "form", "noscript",
                     "iframe", "svg"]):
        tag.decompose()

    # Prefer article/main for cleaner text
    body = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", {"id": re.compile(r"content|main|body", re.I)})
        or soup.find("body")
        or soup
    )

    parts = []
    for el in body.find_all(["h1","h2","h3","h4","p","li","td","th"]):
        t = el.get_text(separator=" ", strip=True)
        if t:
            parts.append(t)

    text = "\n".join(parts) if parts else body.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_text_from_url(url: str, max_depth: int = 2, max_pages: int = 10) -> tuple[str, str]:
    """
    Fetch a URL and return (text, source_name).

    Supports:
      - Direct PDF URLs   → parsed with PyPDF (single page)
      - Regular web pages → crawled recursively with RecursiveUrlLoader

    Parameters
    ----------
    url       : str — the URL to fetch
    max_depth : int — how many link levels deep to crawl (default 2)
    max_pages : int — max number of pages to crawl (default 10)

    Returns
    -------
    text        : str — extracted plain text (all pages joined)
    source_name : str — short label derived from the URL
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # ── Direct PDF link ───────────────────────────────────────────────────────
    try:
        head = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        content_type = head.headers.get("Content-Type", "").lower()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Could not reach URL: {e}")

    if "application/pdf" in content_type or url.lower().endswith(".pdf"):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Could not fetch PDF: {e}")

        reader = PdfReader(BytesIO(response.content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise ValueError("PDF appears to be image-based — no extractable text found.")

        return text.strip(), _url_to_name(url)

    # ── Recursive web crawl ───────────────────────────────────────────────────
    try:
        loader = RecursiveUrlLoader(
            url=url,
            max_depth=max_depth,
            extractor=_bs4_extractor,
            headers=HEADERS,
            timeout=TIMEOUT,
            check_response_status=True,
            continue_on_failure=True,   # skip broken sublinks, don't crash
        )
        docs = loader.load()
    except Exception as e:
        raise ValueError(f"RecursiveUrlLoader failed: {e}")

    if not docs:
        raise ValueError("No content could be extracted from this URL.")

    # Limit to max_pages and join all page texts
    docs = docs[:max_pages]
    pages_text = []
    for doc in docs:
        content = doc.page_content.strip()
        if content:
            # Label each page with its source URL
            source = doc.metadata.get("source", "")
            pages_text.append(f"[Source: {source}]\n{content}")

    text = "\n\n---\n\n".join(pages_text)

    if len(text) < 100:
        raise ValueError(
            "Very little text extracted. The site may block scraping or require login."
        )

    return text, _url_to_name(url)


def _url_to_name(url: str) -> str:
    """Turn a URL into a short readable document name."""
    name = re.sub(r"^https?://", "", url)
    name = name.split("?")[0].split("#")[0]
    parts = [p for p in name.split("/") if p]
    if parts:
        last = parts[-1]
        last = re.sub(r"\.[a-zA-Z]{2,4}$", "", last)
        last = last.replace("-", " ").replace("_", " ").title()
        if last:
            return f"{last} ({parts[0]})"
    return url[:60]