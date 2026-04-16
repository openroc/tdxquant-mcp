from __future__ import annotations

from tdx_mcp.config import get_settings
from tdx_mcp.server.app import create_server


def main() -> None:
    settings = get_settings()
    server = create_server(host=settings.mcp_host, port=settings.mcp_port)
    server.run(transport="sse")


if __name__ == "__main__":
    main()

