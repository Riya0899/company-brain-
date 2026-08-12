import re
import requests
from io import BytesIO
from collections import deque
from urllib.parse import urljoin, urlparse
from pypdf import PdfReader
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from utils.ocr import ocr_image_bytes


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 15


def _same_domain(base_url: str, other_url: str) -> bool:
    b = urlparse(base_url).netloc.replace("www.", "")
    o = urlparse(other_url).netloc.replace("www.", "")
    return b == o


def _extract_tables(soup: BeautifulSoup) -> str:
    tables_text = ""
    for table in soup.find_all("table"):
        tables_text += "\n[TABLE]\n"
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            row_text = " | ".join(c.get_text(strip=True) for c in cells)
            if row_text.strip():
                tables_text += row_text + "\n"
        tables_text += "[/TABLE]\n"
        table.decompose()
    return tables_text


def _extract_images(soup: BeautifulSoup, base_url: str, max_images: int = 6, min_size: int = 60) -> str:
    images_text = ""
    count = 0
    for img in soup.find_all("img"):
        if count >= max_images:
            break
        src = img.get("src")
        if not src:
            continue

        w, h = img.get("width"), img.get("height")
        try:
            if w and int(w) < min_size:
                continue
            if h and int(h) < min_size:
                continue
        except ValueError:
            pass

        img_url = urljoin(base_url, src)
        try:
            resp = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            if "image" not in resp.headers.get("Content-Type", "").lower():
                continue
            ocr_text = ocr_image_bytes(resp.content)
            if ocr_text:
                images_text += f"\n[IMAGE TEXT]\n{ocr_text}\n"
                count += 1
        except Exception:
            continue
    return images_text


def _clean_text(soup: BeautifulSoup) -> str:
    body = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", {"id": re.compile(r"content|main|body", re.I)})
        or soup.find("body")
        or soup
    )

    text = body.get_text(separator="\n", strip=True)

    # Remove extra blank lines
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text.strip()


def _needs_js_render(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    if len(text) < 500:
        return True

    if soup.find(id="root"):
        return True

    if soup.find(id="app"):
        return True

    return False


def _render_with_browser(url: str, browser=None) -> str:
    from playwright.sync_api import sync_playwright

    def _render(b):
        page = b.new_page(user_agent=HEADERS["User-Agent"])
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        html = page.content()
        page.close()
        return html

    if browser is not None:
        return _render(browser)

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            return _render(b)
        finally:
            b.close()


def _get_html(url: str, browser=None) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException as e:
        print(f"Direct fetch blocked for {url} ({e}); trying headless browser instead.")
        return _render_with_browser(url, browser=browser)

    if _needs_js_render(html):
        try:
            html = _render_with_browser(url, browser=browser)
        except Exception as e:
            print(f"Headless render skipped/failed for {url}: {e}")

    return html


def _extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    links = []
    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"]).split("#")[0]
        if full.startswith("http") and _same_domain(base_url, full):
            links.append(full)
    return links


def _process_page(url: str, extract_images: bool = False, browser=None) -> tuple[str, list[str]]:
    
    try:
        html = _get_html(url, browser=browser)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return "", []

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "iframe", "svg"]):
        tag.decompose()

    tables_text = _extract_tables(soup)
    images_text = _extract_images(soup, url) if extract_images else ""
    text = _clean_text(soup)
    links = _extract_links(soup, url)

    combined = f"[Source: {url}]\n{text}\n{tables_text}\n{images_text}".strip()
    return combined, links


def extract_text_from_url(url: str, max_depth: int = 10, max_pages: int = 20) -> tuple[str, str]:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # ── Direct PDF link ──
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

    # ── Crawl the site (BFS, same domain, depth/page-limited) ──
    # ── Crawl the site (BFS, same domain, depth/page-limited) ──
    from playwright.sync_api import sync_playwright

    visited = set()
    queue = deque([(url, 0)])
    pages_text = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            while queue and len(visited) < max_pages:
                current, depth = queue.popleft()
                if current in visited or depth > max_depth:
                    continue
                visited.add(current)

                page_text, links = _process_page(current, extract_images=False, browser=browser)
                if page_text:
                    pages_text.append(page_text)

                if depth < max_depth:
                    for link in links:
                        if link not in visited:
                            queue.append((link, depth + 1))
        finally:
            browser.close()

    text = "\n\n---\n\n".join(pages_text)

    word_count = len(text.split())
    if word_count == 0:
        raise ValueError(
            "Very little meaningful text extracted. The site may block automated "
            "access, require login, or render content our crawler couldn't capture."
        )

    return text, _url_to_name(url)


def _url_to_name(url: str) -> str:
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