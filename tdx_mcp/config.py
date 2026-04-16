from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    tq_path: str
    tq_dll_path: str
    mcp_host: str
    mcp_port: int
    mcp_bearer_token: str


def get_settings() -> Settings:
    tq_path = os.getenv("TQ_PATH", "").strip()
    if not tq_path:
        raise RuntimeError("缺少环境变量 TQ_PATH，请先配置通达信终端策略路径。")

    tq_dll_path = os.getenv("TQ_DLL_PATH", "").strip()
    mcp_host = os.getenv("MCP_HOST", "127.0.0.1").strip() or "127.0.0.1"
    mcp_port = int(os.getenv("MCP_PORT", "8765"))
    mcp_bearer_token = os.getenv("MCP_BEARER_TOKEN", "").strip()

    return Settings(
        tq_path=tq_path,
        tq_dll_path=tq_dll_path,
        mcp_host=mcp_host,
        mcp_port=mcp_port,
        mcp_bearer_token=mcp_bearer_token,
    )

