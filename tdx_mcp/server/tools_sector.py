from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_sector_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="sector_list")
    def sector_list(
        list_type: Annotated[
            int,
            Field(
                description=(
                    "板块列表分类整型，默认 0；推荐取值见 schema VALID_LIST_TYPES。"
                    "具体含义（行业/概念/地域等）以通达信 list_sector(list_type) 文档与终端为准。"
                )
            ),
        ] = 0,
    ) -> list[dict]:
        """板块数据：获取板块列表（tqcenter.list_sector）。"""
        return service.list_sector(list_type=list_type)

    @mcp.tool(name="sector_stocks")
    def sector_stocks(
        block_code: Annotated[str, Field(description="板块代码或简称（与 sector_list 返回字段对应，参见终端）。")],
        block_type: Annotated[
            int,
            Field(description="0 普通板块；1 按板块代码解析；2 期货板块。对应 schema VALID_BLOCK_TYPES={0,1,2}。"),
        ] = 0,
        list_type: Annotated[
            int,
            Field(description="成分股列表展示类型整型，默认 0；推荐取值见 schema VALID_LIST_TYPES，细分含义以终端为准。"),
        ] = 0,
    ) -> list[dict]:
        """板块数据：获取指定板块成分股。"""
        return service.list_sector_stocks(block_code=block_code, block_type=block_type, list_type=list_type)

    @mcp.tool(name="sector_user_list")
    def sector_user_list() -> list[dict]:
        """板块数据：获取用户自选板块列表。"""
        return service.list_user_sector()

    @mcp.tool(name="sector_get_relation")
    def sector_get_relation(
        stock_code: Annotated[str, Field(description='证券代码，如 "600519.SH"（validate_symbol）。')]
    ) -> list[dict]:
        """板块数据：查询单股所属板块/主题关系。"""
        return service.get_relation(stock_code=stock_code)

