from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_cb_ipo_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="cbipo_get_kzz_info")
    def cbipo_get_kzz_info(
        stock_code: Annotated[
            str,
            Field(description='可转债代码，如 "113050.SH"；格式同 validate_symbol（后缀大写）。'),
        ],
        field_list: Annotated[
            list[str] | None,
            Field(description="转债信息字段子集；留空返回终端默认列。"),
        ] = None,
    ) -> dict:
        """可转债/新股：可转债基础信息（get_kzz_info）。"""
        return service.get_kzz_info(stock_code=stock_code, field_list=field_list)

    @mcp.tool(name="cbipo_get_ipo_info")
    def cbipo_get_ipo_info(
        ipo_type: Annotated[
            int,
            Field(
                description=(
                    "新股信息类型整型，默认 0；当前 schema 常量 VALID_IPO_TYPES={0}。"
                    "细分类型（沪深/科创板等）以 tqcenter.get_ipo_info 与终端为准。"
                )
            ),
        ] = 0,
        ipo_date: Annotated[
            int,
            Field(description="申购日或查询日 YYYYMMDD（整数），如 20250416；0 表示由终端默认规则处理。"),
        ] = 0,
    ) -> list[dict]:
        """可转债/新股：新股申购/发行信息列表。"""
        return service.get_ipo_info(ipo_type=ipo_type, ipo_date=ipo_date)

