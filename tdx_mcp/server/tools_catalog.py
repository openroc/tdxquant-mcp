from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from tdx_mcp.server.category_registry import build_catalog
from tdx_mcp.server.tool_metadata import TOOL_METADATA
from tdx_mcp.schema.params import (
    SUPPORTED_STOCK_SUFFIXES,
    VALID_BLOCK_TYPES,
    VALID_DIVIDEND_TYPES,
    VALID_FORMULA_MODES,
    VALID_IPO_TYPES,
    VALID_LIST_TYPES,
    VALID_MARKETS,
    VALID_ORDER_TYPES,
    VALID_PERIODS,
    VALID_PRICE_TYPES,
    VALID_REPORT_TYPES,
)


def get_enum_definitions() -> dict[str, list[str]]:
    """集中输出 MCP 常用枚举定义（来自 schema.params）。"""
    return {
        "supported_stock_suffixes": sorted(SUPPORTED_STOCK_SUFFIXES),
        "valid_periods": sorted(VALID_PERIODS),
        "valid_dividend_types": sorted(VALID_DIVIDEND_TYPES),
        "valid_report_types": sorted(VALID_REPORT_TYPES),
        "valid_formula_modes": sorted(VALID_FORMULA_MODES),
        "valid_order_types": sorted(VALID_ORDER_TYPES),
        "valid_price_types": sorted(VALID_PRICE_TYPES),
        "valid_block_types": sorted(VALID_BLOCK_TYPES),
        "valid_list_types": sorted(VALID_LIST_TYPES),
        "valid_markets": sorted(VALID_MARKETS),
        "valid_ipo_types": sorted(VALID_IPO_TYPES),
    }


def register_catalog_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="tools_catalog")
    def tools_catalog() -> dict:
        """
        返回当前 MCP 工具分类目录（与 tool_metadata 及 category_registry 一致）。
        结构通常包含：按「连接管理/行情数据/…」等分类汇总的摘要，以及每类下工具名称与一句 summary；
        具体键名以 build_catalog 实现为准。用于先浏览分类再调用具体工具名。
        """
        return build_catalog(TOOL_METADATA)

    @mcp.tool(name="tools_enum_definitions")
    def tools_enum_definitions(
        enum_name: Annotated[
            str,
            Field(
                description=(
                    "可选枚举名：supported_stock_suffixes / valid_periods / "
                    "valid_dividend_types / valid_report_types / valid_formula_modes / "
                    "valid_order_types / valid_price_types / valid_block_types / "
                    "valid_list_types / valid_markets / valid_ipo_types；"
                    "留空返回全部。"
                )
            ),
        ] = "",
    ) -> dict:
        """返回工具参数可用枚举定义（对齐 schema.params 常量）。"""
        enum_map = get_enum_definitions()
        key = enum_name.strip().lower()
        if not key:
            return {"enums": enum_map}
        if key not in enum_map:
            return {
                "error": f"未知枚举名: {enum_name}",
                "available": sorted(enum_map.keys()),
            }
        return {key: enum_map[key]}

