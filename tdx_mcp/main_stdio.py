from __future__ import annotations

from tdx_mcp.server.app import create_server


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

