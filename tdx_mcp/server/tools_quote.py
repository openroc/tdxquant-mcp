from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_quote_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="market_get_kline")
    def market_get_kline(
        stock_list: Annotated[
            list[str],
            Field(
                description='证券代码列表，每项形如 "600519.SH"（后缀大写；A股为6位数字）。与 schema.params.validate_symbol 规则一致。'
            ),
        ],
        period: Annotated[
            str,
            Field(
                description="K线/Tick 周期，须为下列之一（大小写不敏感）：tick, 1m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1mon, 45d, 1q, 1y。"
            ),
        ],
        field_list: Annotated[
            list[str] | None,
            Field(
                description="返回字段子集；留空或 None 表示全部字段。结果在服务端按字段名大小写不敏感过滤（与底层返回键匹配）。"
            ),
        ] = None,
        start_time: Annotated[
            str,
            Field(description="起始时间：YYYYMMDD 或 YYYYMMDDHHMMSS；可与 end_time、count 组合，具体优先级以通达信 tqcenter 为准。"),
        ] = "",
        end_time: Annotated[
            str,
            Field(description="结束时间：YYYYMMDD 或 YYYYMMDDHHMMSS；空字符串表示不限制结束时刻。"),
        ] = "",
        count: Annotated[
            int,
            Field(
                description="取最近 N 根 K 线（或 N 条 tick）；>0 时通常按条数从结束时间向前取，-1 表示主要依赖起止时间区间（以终端行为为准）。"
            ),
        ] = -1,
        dividend_type: Annotated[
            str | None,
            Field(
                description="除权复权：none（不复权，默认）、front（前复权）、back（后复权）。未传或 None 时按 none 处理。"
            ),
        ] = None,
        fill_data: Annotated[bool, Field(description="是否对缺失 K 线进行填充（通达信 fill_data）。")] = True,
    ) -> dict:
        """行情数据：获取 K 线或分笔（tick）。period=tick 时为分笔数据。"""
        return service.get_market_data(
            stock_list=stock_list,
            period=period,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            fill_data=fill_data,
        )

    @mcp.tool(name="market_get_snapshot")
    def market_get_snapshot(
        stock_code: Annotated[
            str,
            Field(description='单只证券代码，例如 "600519.SH"（后缀大写，与 validate_symbol 一致）。'),
        ],
        field_list: Annotated[
            list[str] | None,
            Field(description="快照字段子集；留空返回终端提供的全部字段（直接传入 tqcenter，无大小写过滤）。"),
        ] = None,
    ) -> dict:
        """行情数据：获取实时行情快照（单代码）。"""
        return service.get_market_snapshot(stock_code=stock_code, field_list=field_list)

    @mcp.tool(name="market_subscribe_hq")
    def market_subscribe_hq(
        stock_list: Annotated[
            list[str],
            Field(description='订阅的证券代码列表，格式同 market_get_kline（如 ["600519.SH"]）。MCP 使用占位回调，不推送事件到会话。'),
        ]
    ) -> dict:
        """行情数据：订阅行情更新（MCP 内为占位回调，仅完成终端侧订阅）。"""
        return service.subscribe_hq(stock_list=stock_list)

