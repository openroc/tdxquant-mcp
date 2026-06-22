#!/usr/bin/env python3
"""
Breadth-first crawl of help.tdx.com.cn/quant/docs/, write Markdown mirror + manifest.

  uv sync --extra sync-docs
  python scripts/sync_tdx_help_docs.py [--out DIR] [--max-pages N] [--delay SEC] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import hashlib
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from tdx_mcp.sync_help import (
    ALLOWED_HOST,
    PATH_PREFIX,
    canonical_url,
    dedup_key,
    extract_doc_links,
    html_to_markdown,
    is_under_quant_docs,
    page_title_from_html,
    path_to_filename,
)

DEFAULT_USER_AGENT = "TdxQuantDocsMirror/1.0 (local documentation sync; +https://help.tdx.com.cn/)"
# 根路径 /quant/docs/ 对匿名请求常返回 403；从官方「简介」入口即可 BFS 覆盖子站。
DEFAULT_SEEDS = [
    f"https://{ALLOWED_HOST}{PATH_PREFIX}/markdown/mindoc-1cfsjkbf8f3is/",
]


def load_robots(client: httpx.Client, ignore: bool) -> tuple[RobotFileParser | None, bool]:
    """
    Returns (parser, missing_file).
    missing_file is True when robots.txt returned 404 (crawl without rules).
    """
    if ignore:
        return None, False
    url = f"https://{ALLOWED_HOST}/robots.txt"
    r = client.get(url)
    if r.status_code == 404:
        return None, True
    r.raise_for_status()
    rp = RobotFileParser()
    rp.set_url(url)
    rp.parse(r.text.splitlines())
    return rp, False


def can_fetch(rp: RobotFileParser | None, ua: str, url: str) -> bool:
    if rp is None:
        return True
    return rp.can_fetch(ua, url)


def yaml_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_page(
    out_pages: Path,
    title: str,
    source_url: str,
    fetched_at: str,
    body_md: str,
) -> str:
    front = (
        "---\n"
        f'title: "{yaml_escape(title)}"\n'
        f"source_url: {source_url}\n"
        f"fetched_at: {fetched_at}\n"
        "---\n\n"
    )
    rel = path_to_filename(source_url)
    path = out_pages / rel
    path.write_text(front + body_md + "\n", encoding="utf-8")
    return f"pages/{rel}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror TdxQuant online help under quant/docs.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/mirror-tdx-quant-help"),
        help="Output directory (default: docs/mirror-tdx-quant-help)",
    )
    parser.add_argument("--max-pages", type=int, default=500, help="Max HTML pages to fetch")
    parser.add_argument("--delay", type=float, default=0.75, help="Seconds between requests")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Skip robots.txt check (not recommended for routine use)",
    )
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP User-Agent")
    args = parser.parse_args()

    out: Path = args.out
    pages_dir = out / "pages"
    if not args.dry_run:
        pages_dir.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": args.user_agent}
    manifest_entries: list[dict] = []
    errors: list[dict] = []

    with httpx.Client(timeout=45.0, follow_redirects=True, headers=headers) as client:
        try:
            rp, robots_missing = load_robots(client, args.ignore_robots)
            if robots_missing:
                print("Note: robots.txt not found (404); crawling without robots rules.", file=sys.stderr)
        except Exception as e:
            print(f"robots.txt failed: {e}; use --ignore-robots to override.", file=sys.stderr)
            return 2

        seen: set[str] = set()
        fetched_final: set[str] = set()
        queue: deque[str] = deque()
        for s in DEFAULT_SEEDS:
            k = dedup_key(s)
            if k not in seen and is_under_quant_docs(s) and can_fetch(rp, args.user_agent, s):
                seen.add(k)
                queue.append(canonical_url(s))

        while queue and len(manifest_entries) < args.max_pages:
            url = queue.popleft()
            if not can_fetch(rp, args.user_agent, url):
                errors.append({"url": url, "error": "blocked_by_robots"})
                continue
            try:
                resp = client.get(url)
            except httpx.HTTPError as e:
                errors.append({"url": url, "error": str(e)})
                time.sleep(args.delay)
                continue

            final_url = canonical_url(str(resp.url))
            ct = (resp.headers.get("content-type") or "").lower()

            if resp.status_code != 200:
                errors.append({"url": final_url, "status": resp.status_code})
                time.sleep(args.delay)
                continue

            if "text/html" not in ct and "html" not in ct:
                time.sleep(args.delay)
                continue

            if final_url in fetched_final:
                time.sleep(args.delay)
                continue

            html = resp.text
            for link in extract_doc_links(html, final_url):
                lk = dedup_key(link)
                if lk not in seen and is_under_quant_docs(link) and can_fetch(rp, args.user_agent, link):
                    seen.add(lk)
                    queue.append(canonical_url(link))

            title_fallback = urlparse(final_url).path.rstrip("/").split("/")[-1] or "untitled"
            title_guess = page_title_from_html(html, title_fallback)
            body_md, meta_title = html_to_markdown(html, final_url)
            title = (meta_title or title_guess or title_fallback).strip()
            if title.startswith("#"):
                title = title.lstrip("#").strip() or title_fallback

            fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            sha = hashlib.sha256(body_md.encode("utf-8")).hexdigest()
            rel_path = f"pages/{path_to_filename(final_url)}"

            if not args.dry_run:
                rel_path = write_page(pages_dir, title, final_url, fetched_at, body_md)

            fetched_final.add(final_url)
            manifest_entries.append(
                {
                    "url": final_url,
                    "title": title,
                    "file": rel_path,
                    "status": resp.status_code,
                    "content_sha256": sha,
                }
            )
            print(f"OK {len(manifest_entries)} {final_url}")
            time.sleep(args.delay)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "generated_at": generated_at,
        "source": f"https://{ALLOWED_HOST}{PATH_PREFIX}/",
        "entries": sorted(manifest_entries, key=lambda x: x["title"].lower()),
        "errors": errors,
    }

    readme_lines = [
        "# 通达信量化在线帮助（本地镜像）",
        "",
        "> **版权声明**：正文转载自通达信官方帮助站点，版权归深圳市财富趋势科技股份有限公司所有。"
        " **请以在线版为准**：",
        f"> https://{ALLOWED_HOST}{PATH_PREFIX}/",
        "",
        f"本目录由仓库脚本 `scripts/sync_tdx_help_docs.py` 于 **{generated_at}** 生成。",
        "请勿将本镜像作为官方文档对外分发；仅供本地学习与开发辅助。",
        "",
        "## 页面索引（按标题排序）",
        "",
    ]
    for e in manifest["entries"]:
        readme_lines.append(f"- [{e['title']}]({e['file']}) — `{e['url']}`")
    if errors:
        readme_lines.extend(["", "## 抓取异常", ""])
        for err in errors:
            readme_lines.append(f"- `{err.get('url', '')}`: {err}")

    if not args.dry_run:
        (out / "_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (out / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    print(f"Done. pages={len(manifest_entries)} errors={len(errors)} out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
