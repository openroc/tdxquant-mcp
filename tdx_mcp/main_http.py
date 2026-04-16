from __future__ import annotations

import asyncio
import sys
from http import HTTPStatus

from mcp.server.fastmcp import FastMCP, Context

from tdx_mcp.config import get_settings
from tdx_mcp.server.app import create_server


def _format_base_url(host: str, port: int) -> str:
    display_host = host
    if host == "0.0.0.0":
        display_host = "127.0.0.1"
    return f"http://{display_host}:{port}"


def _shutdown_server(server: FastMCP | None) -> None:
    if server is None:
        return
    service = getattr(server, "_tdx_service", None)
    if service is None:
        return
    try:
        service.close()
    except Exception as exc:
        print(f"[tdxquant-mcp] 关闭 TdxQuant 连接时发生异常：{exc}", file=sys.stderr)


def _create_sse_endpoint(server: FastMCP) -> None:
    """创建自定义 SSE 端点，支持 OPTIONS 预检请求。"""
    from starlette.responses import Response
    
    # 获取底层 transport（Starlette/FastAPI）
    if hasattr(server, '_transport') and server._transport is not None:
        transport = server._transport
        
        @transport.route("/sse", methods=["OPTIONS", "POST"])
        async def sse_handler(request):
            response = Response()
            
            # CORS 响应头
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
            response.headers["Allow"] = "GET, POST, OPTIONS"
            
            if request.method == "OPTIONS":
                # 预检请求，立即返回
                return response
                
            elif request.method == "POST":
                # SSE 流式响应
                async def sse_stream():
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except Exception as e:
                        pass
                
                response.headers["Content-Type"] = "text/event-stream"
                response.headers["Cache-Control"] = "no-cache"
                response.headers["Connection"] = "keep-alive"
                return Response(sse_stream())
            
            return response
    
    # 备用方案：如果 server 是 FastAPI 实例，使用 add_api_route
    elif hasattr(server, 'add_api_route'):
        @server.add_api_route("/sse", methods=["GET", "POST"], include_in_schema=False)
        async def sse_endpoint():
            # SSE 实现...
            pass


def main() -> None:
    server: FastMCP | None = None
    try:
        settings = get_settings()
        base_url = _format_base_url(settings.mcp_host, settings.mcp_port)
        print("[tdxquant-mcp] 正在初始化 HTTP/SSE 服务...")
        mcp_server = create_server(host=settings.mcp_host, port=settings.mcp_port)

        # 注册自定义 SSE 端点
        _create_sse_endpoint(mcp_server)

        print(f"[tdxquant-mcp] 服务已启动：{base_url}")
        print(f"[tdxquant-mcp] SSE 端点：{base_url}/sse")
        if settings.mcp_bearer_token:
            print("[tdxquant-mcp] 鉴权：已启用 Bearer Token")
        else:
            print("[tdxquant-mcp] 鉴权：未启用")
        print("[tdxquant-mcp] 按 Ctrl+C 可优雅关闭服务")
        mcp_server.run(transport="sse")
    except KeyboardInterrupt:
        print("\n[tdxquant-mcp] 收到 Ctrl+C，正在优雅关闭...")
    except Exception as exc:
        print(f"[tdxquant-mcp] 服务启动失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        _shutdown_server(server)
        if server is not None:
            print("[tdxquant-mcp] 服务已关闭")


if __name__ == "__main__":
    main()

