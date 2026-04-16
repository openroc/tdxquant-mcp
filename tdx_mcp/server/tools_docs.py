from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

TDXQUANT_INTRO_SOURCE_URL = "https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/"


def _load_tdxquant_intro_markdown() -> str:
    path = Path(__file__).resolve().parent.parent / "resources" / "tdxquant_intro.md"
    return path.read_text(encoding="utf-8")


def register_docs_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="docs_get_tdxquant_intro")
    def docs_get_tdxquant_intro() -> dict[str, Any]:
        """
        返回《TdxQuant 简介》整理稿（Markdown）：平台定位、运行环境、tqcenter 能力、
        回测/预警/交易场景及官方文档导航。不依赖通达信连接；正文来自包内 resources/tdxquant_intro.md。
        字段 source_url 为在线帮助原始入口；本地镜像可参考项目 docs/mirror-tdx-quant-help/。
        """
        return {
            "title": "TdxQuant 简介",
            "source_url": TDXQUANT_INTRO_SOURCE_URL,
            "content_format": "markdown",
            "content": _load_tdxquant_intro_markdown(),
        }
