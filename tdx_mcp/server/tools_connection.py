from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_connection_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="connection_initialize")
    def connection_initialize() -> dict:
        """
        连接管理：主动初始化与通达信终端的 tqcenter 连接。
        前置条件：本机已安装并启动支持 TdxQuant 的通达信客户端；若使用自定义安装路径，请配置环境变量 TQ_PATH（见包内 README/简介）。
        """
        return service.initialize_connection()

    @mcp.tool(name="connection_close")
    def connection_close() -> dict:
        """连接管理：关闭当前 tqcenter 会话/连接；之后查询类工具需先重新 initialize。"""
        return service.close_connection()

