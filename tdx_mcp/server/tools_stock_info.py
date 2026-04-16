from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_stock_info_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="stock_get_info")
    def stock_get_info(
        stock_code: Annotated[str, Field(description='证券代码，如 "600519.SH"。')],
        field_list: Annotated[
            list[str] | None,
            Field(description="基础信息字段子集；留空返回终端默认全部字段（直接传 tqcenter）。"),
        ] = None,
    ) -> dict:
        """股票信息：F10 类基础信息（get_stock_info）。"""
        return service.get_stock_info(stock_code=stock_code, field_list=field_list)

    @mcp.tool(name="stock_get_more_info")
    def stock_get_more_info(
        stock_code: Annotated[str, Field(description='证券代码，如 "600519.SH"。')],
        field_list: Annotated[
            list[str] | None,
            Field(description="扩展信息字段子集；留空返回默认列。"),
        ] = None,
    ) -> dict:
        """股票信息：更多扩展信息（get_more_info）。"""
        return service.get_more_info(stock_code=stock_code, field_list=field_list)

    @mcp.tool(name="stock_get_capital_info")
    def stock_get_capital_info(
        stock_code: Annotated[str, Field(description='证券代码，如 "600519.SH"。')],
        date_list: Annotated[
            list[str],
            Field(description="查询日期列表，每项为 YYYYMMDD 字符串；用于股本变更历史查询。"),
        ],
        count: Annotated[
            int,
            Field(description="从 date_list 中取最近 count 个日期的股本数据；须 <= len(date_list)。"),
        ] = 1,
    ) -> dict:
        """股票信息：股本结构（get_gb_info）。"""
        return service.get_gb_info(stock_code=stock_code, date_list=date_list, count=count)

    @mcp.tool(name="stock_get_track_etf_info")
    def stock_get_track_etf_info(
        zs_code: Annotated[str, Field(description='指数代码，格式同证券代码，如 "000300.SH"。')]
    ) -> dict:
        """股票信息：查询跟踪该指数的 ETF 列表与跟踪信息。"""
        return service.get_track_etf_info(zs_code=zs_code)

