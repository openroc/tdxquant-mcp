from __future__ import annotations

import asyncio
import sys
from http import HTTPStatus
from typing import Any

from mcp.server.fastmcp import FastMCP, Context
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

from tdx_mcp.config import get_settings
from tdx_mcp.server.app import create_server


class CORSASGIMiddleware:
    """自定义 ASGI 中间件，确保所有响应都包含 CORS 头。"""
    
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 处理 OPTIONS 预检请求
        if scope.get("method") == "OPTIONS":
            headers = [
                (b"access-control-allow-origin", b"*"),
                (b"access-control-allow-methods", b"GET, POST, OPTIONS"),
                (b"access-control-allow-headers", b"*"),
                (b"access-control-max-age", b"86400"),
            ]
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
            })
            await send({
                "type": "http.response.body",
                "body": b"",
            })
            return
        
        # 包装 send 函数，为所有响应添加 CORS 头
        async def send_with_cors(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                # 添加 CORS 头
                headers.append((b"access-control-allow-origin", b"*"))
                headers.append((b"access-control-allow-methods", b"GET, POST, OPTIONS"))
                headers.append((b"access-control-allow-headers", b"*"))
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_with_cors)


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
    
    # 方法1: 尝试给 server 直接添加 CORS 中间件
    if hasattr(server, 'add_middleware'):
        server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=86400,
        )
        print("[tdxquant-mcp] 已添加 CORS 中间件到 FastMCP server")
    
    # 方法2: 尝试获取底层 transport 并添加中间件
    if hasattr(server, '_transport') and server._transport is not None:
        transport = server._transport
        
        # 尝试获取底层的 Starlette 应用
        starlette_app = None
        if hasattr(transport, 'app'):
            starlette_app = transport.app
        elif hasattr(transport, '_app'):
            starlette_app = transport._app
        
        # 添加 CORS 中间件
        if starlette_app is not None and hasattr(starlette_app, 'add_middleware'):
            starlette_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
                allow_headers=["*"],
                expose_headers=["*"],
                max_age=86400,
            )
            print("[tdxquant-mcp] 已添加 CORS 中间件到 Starlette app")
        
        @transport.route("/sse", methods=["GET", "OPTIONS", "POST"])
        async def sse_handler(request):
            # OPTIONS 预检请求直接返回
            if request.method == "OPTIONS":
                from starlette.responses import PlainTextResponse
                return PlainTextResponse(
                    content="",
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "86400",
                    }
                )
            
            # SSE 流式响应
            async def sse_stream():
                try:
                    while True:
                        await asyncio.sleep(1)
                except Exception:
                    pass
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                sse_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                }
            )
    
    # 备用方案：如果 server 是 FastAPI 实例，使用 add_api_route
    elif hasattr(server, 'add_api_route'):
        from starlette.responses import PlainTextResponse, StreamingResponse
        
        # 添加 CORS 中间件
        server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=86400,
        )
        print("[tdxquant-mcp] 已添加 CORS 中间件到 FastAPI server")
        
        @server.add_api_route("/sse", methods=["GET", "OPTIONS", "POST"], include_in_schema=False)
        async def sse_endpoint(request):
            # OPTIONS 预检请求直接返回
            if request.method == "OPTIONS":
                return PlainTextResponse(
                    content="",
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "86400",
                    }
                )
            
            # SSE 实现
            async def sse_stream():
                try:
                    while True:
                        await asyncio.sleep(1)
                except Exception:
                    pass
            
            return StreamingResponse(
                sse_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                }
            )


def main() -> None:
    mcp_server = None
    try:
        settings = get_settings()
        base_url = _format_base_url(settings.mcp_host, settings.mcp_port)
        print("[tdxquant-mcp] 正在初始化 HTTP/SSE 服务...")
        mcp_server = create_server(host=settings.mcp_host, port=settings.mcp_port)

        # 注册自定义 SSE 端点（包含 CORS 中间件）
        _create_sse_endpoint(mcp_server)
        
        # 获取 SSE app 并包装 CORS 中间件
        sse_app = mcp_server.sse_app()
        
        # 添加 OAuth 资源发现端点（避免 404 错误）
        from starlette.routing import Route
        from starlette.responses import PlainTextResponse, JSONResponse
        
        async def oauth_protected_resource_handler(request):
            """处理 OAuth 资源发现请求。"""
            return JSONResponse(
                status_code=200,
                content={
                    "resource": f"http://{settings.mcp_host}:{settings.mcp_port}/sse",
                    "authorization_servers": [],
                    "scopes_supported": [],
                    "bearer_methods_supported": ["header"],
                    "resource_documentation": "This service does not require OAuth authentication"
                },
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # 添加两个 OAuth 发现端点路由
        oauth_root_route = Route(
            "/.well-known/oauth-protected-resource",
            oauth_protected_resource_handler,
            methods=["GET"]
        )
        oauth_sse_route = Route(
            "/.well-known/oauth-protected-resource/sse",
            oauth_protected_resource_handler,
            methods=["GET"]
        )
        sse_app.routes.append(oauth_root_route)
        sse_app.routes.append(oauth_sse_route)
        
        # 添加 POST 方法支持到 /sse 路由
        
        async def sse_post_handler(request):
            """处理 POST 请求，避免 405 错误。"""
            # 可以根据需要添加 POST 处理逻辑
            # 目前返回 200 表示接受请求
            return PlainTextResponse(
                content="POST received",
                status_code=200,
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # 添加 POST 路由
        post_route = Route("/sse", sse_post_handler, methods=["POST"])
        sse_app.routes.append(post_route)
        
        # 应用 CORS 中间件
        app_with_cors = CORSASGIMiddleware(sse_app)
        
        print(f"[tdxquant-mcp] 服务已启动：{base_url}")
        print(f"[tdxquant-mcp] SSE 端点：{base_url}/sse")
        print(f"[tdxquant-mcp] 支持方法：GET, POST, OPTIONS")
        if settings.mcp_bearer_token:
            print("[tdxquant-mcp] 鉴权：已启用 Bearer Token")
        else:
            print("[tdxquant-mcp] 鉴权：未启用")
        print("[tdxquant-mcp] 按 Ctrl+C 可优雅关闭服务")
        print("[tdxquant-mcp] 已应用全局 CORS 中间件")
        
        # 使用 Uvicorn 启动
        import uvicorn
        uvicorn.run(
            app_with_cors,
            host=settings.mcp_host,
            port=settings.mcp_port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[tdxquant-mcp] 收到 Ctrl+C，正在优雅关闭...")
    except Exception as exc:
        print(f"[tdxquant-mcp] 服务启动失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        _shutdown_server(mcp_server)
        if mcp_server is not None:
            print("[tdxquant-mcp] 服务已关闭")


if __name__ == "__main__":
    main()

