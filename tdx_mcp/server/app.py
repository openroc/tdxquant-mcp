from __future__ import annotations

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

from tdx_mcp.config import get_settings
from tdx_mcp.server.auth import StaticBearerTokenVerifier
from tdx_mcp.server.tools_calendar import register_calendar_tools
from tdx_mcp.server.tools_cb_ipo import register_cb_ipo_tools
from tdx_mcp.server.tools_catalog import register_catalog_tools
from tdx_mcp.server.tools_connection import register_connection_tools
from tdx_mcp.server.tools_docs import register_docs_tools
from tdx_mcp.server.tools_financial import register_financial_tools
from tdx_mcp.server.tools_quote import register_quote_tools
from tdx_mcp.server.tools_sector import register_sector_tools
from tdx_mcp.server.tools_stock_info import register_stock_info_tools
from tdx_mcp.server.tools_trade import register_trade_tools
from tdx_mcp.server.tools_utility_cache import register_utility_cache_tools
from tdx_mcp.service.tdx_service import TdxQuantService


def create_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    settings = get_settings()
    service = TdxQuantService(tq_path=settings.tq_path, tq_dll_path=settings.tq_dll_path)
    service.initialize()
    token_verifier = None
    auth_settings = None
    if settings.mcp_bearer_token:
        token_verifier = StaticBearerTokenVerifier(settings.mcp_bearer_token)
        # Enable FastMCP auth gate. Real token validation is done by token_verifier.
        auth_settings = AuthSettings(issuer_url="http://127.0.0.1")

    mcp = FastMCP(
        name="通达信量化 MCP 服务",
        instructions=(
            "这是一个基于 TdxQuant/tqcenter 的中文量化数据 MCP 服务。"
            "可用于获取行情快照、K线/Tick、财务数据、板块成分股，以及执行通达信公式。"
            "可先调用 tools_catalog 查看工具分类；不了解 TdxQuant 时可调用 docs_get_tdxquant_intro 阅读平台简介。"
            "常用代码示例：贵州茅台为 600519.SH。"
        ),
        host=host,
        port=port,
        auth=auth_settings,
        token_verifier=token_verifier,
    )
    register_connection_tools(mcp, service)
    register_quote_tools(mcp, service)
    register_stock_info_tools(mcp, service)
    register_sector_tools(mcp, service)
    register_financial_tools(mcp, service)
    register_cb_ipo_tools(mcp, service)
    register_calendar_tools(mcp, service)
    register_trade_tools(mcp, service)
    register_utility_cache_tools(mcp, service)
    register_catalog_tools(mcp)
    register_docs_tools(mcp)
    return mcp

