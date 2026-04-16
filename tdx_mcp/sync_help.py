"""Helpers for mirroring help.tdx.com.cn quant docs (testable, no I/O)."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

ALLOWED_HOST = "help.tdx.com.cn"
PATH_PREFIX = "/quant/docs"
SKIP_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".css",
    ".js",
    ".woff",
    ".woff2",
    ".ttf",
    ".zip",
    ".pdf",
    ".mp4",
)

_BAD_FS_CHARS = re.compile(r'[<>:"|?*\\]')


def canonical_url(url: str) -> str:
    """Strip fragment, lowercase host; normalize trailing slashes (docs root keeps /)."""
    p = urlparse(url)
    path = p.path or "/"
    if path.rstrip("/") == PATH_PREFIX:
        path = PATH_PREFIX + "/"
    elif len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    netloc = (p.netloc or "").lower()
    return urlunparse((p.scheme, netloc, path, p.params, p.query, ""))


def dedup_key(url: str) -> str:
    """Key for visited set (scheme + host + path + query, no fragment)."""
    return canonical_url(url)


def is_under_quant_docs(url: str) -> bool:
    p = urlparse(url)
    host = (p.netloc or "").lower()
    if host and host != ALLOWED_HOST:
        return False
    path = p.path or "/"
    return path == PATH_PREFIX or path.startswith(PATH_PREFIX + "/")


def should_skip_href(path: str) -> bool:
    lower = path.lower().split("?", 1)[0]
    return any(lower.endswith(ext) for ext in SKIP_EXTENSIONS)


def extract_doc_links(html: str, base_url: str) -> list[str]:
    """Return absolute http(s) URLs under /quant/docs/ found in HTML."""
    soup = BeautifulSoup(html, "html.parser")
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        raw = a["href"].strip()
        if not raw or raw.startswith(("#", "javascript:", "mailto:", "data:")):
            continue
        joined = urljoin(base_url, raw)
        p = urlparse(joined)
        if p.scheme not in ("http", "https"):
            continue
        host = (p.netloc or "").lower()
        if host and host != ALLOWED_HOST:
            continue
        path = p.path or "/"
        if should_skip_href(path):
            continue
        if not (path == PATH_PREFIX or path.startswith(PATH_PREFIX + "/")):
            continue
        clean = urlunparse((p.scheme, ALLOWED_HOST, path, "", p.query, ""))
        out.append(clean)
    return out


def path_to_filename(url: str, max_stem: int = 160) -> str:
    """Stable .md filename from URL path (filesystem-safe, bounded length)."""
    p = urlparse(url)
    path = p.path or "/"
    if path.startswith(PATH_PREFIX):
        rel = path[len(PATH_PREFIX) :].lstrip("/")
    else:
        rel = path.lstrip("/")
    if not rel:
        rel = "index"
    stem = rel.replace("/", "__")
    stem = _BAD_FS_CHARS.sub("_", stem)
    stem = stem.strip("._") or "page"
    if p.query:
        q = hashlib.sha256(p.query.encode("utf-8")).hexdigest()[:8]
        stem = f"{stem}__q_{q}"
    if len(stem) > max_stem:
        h = hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]
        stem = f"{stem[: max_stem // 2]}__{h}"
    return stem + ".md"


def html_to_markdown(html: str, url: str) -> tuple[str, str | None]:
    """
    Returns (markdown, title_hint).
    Uses trafilatura first, then html2text on body.
    """
    import html2text
    import trafilatura

    title_hint: str | None = None
    meta = trafilatura.extract_metadata(html)
    if meta and meta.title:
        title_hint = meta.title.strip() or None

    md = trafilatura.extract(
        html,
        output_format="markdown",
        url=url,
        include_comments=False,
        include_tables=True,
    )
    if md and md.strip():
        return md.strip(), title_hint

    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string and not title_hint:
        title_hint = soup.title.string.strip() or None
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body = soup.body
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    raw = h.handle(str(body) if body else str(soup))
    return (raw.strip() or "(empty)"), title_hint


def page_title_from_html(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        t = soup.title.string.strip()
        if t:
            return t
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    return fallback
