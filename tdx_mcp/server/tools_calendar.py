from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_calendar_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="calendar_get_trading_calendar")
    def calendar_get_trading_calendar(
        market: Annotated[
            str,
            Field(description="市场标识，如 AG（A股）、HK、US；对应 schema VALID_MARKETS。"),
        ],
        start_time: Annotated[str, Field(description="区间起点：YYYYMMDD 或 YYYYMMDDHHMMSS。")],
        end_time: Annotated[str, Field(description="区间终点：YYYYMMDD 或 YYYYMMDDHHMMSS（含边界规则以终端为准）。")],
    ) -> list[str]:
        """交易日历：返回指定市场、时间段内的交易日列表（通常为 YYYYMMDD 字符串）。"""
        return service.get_trading_calendar(market=market, start_time=start_time, end_time=end_time)

