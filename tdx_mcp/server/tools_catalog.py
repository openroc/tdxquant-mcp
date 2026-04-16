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


def get_enum_definitions() -> dict[str, list[dict[str, str]]]:
    """集中输出 MCP 常用枚举定义（来自 schema.params），包含中文注释。"""
    return {
        "supported_stock_suffixes": [
            {"value": "SH", "description": "上海证券交易所"},
            {"value": "SZ", "description": "深圳证券交易所"},
            {"value": "BJ", "description": "北京证券交易所"},
            {"value": "HK", "description": "港股"},
            {"value": "US", "description": "美股"},
            {"value": "NQ", "description": "全国股转系统（新三板）"},
            {"value": "SHO", "description": "上证期权"},
            {"value": "SZO", "description": "深证期权"},
            {"value": "CFF", "description": "中金所期货"},
            {"value": "SHF", "description": "上期所期货"},
            {"value": "DCE", "description": "大商所期货"},
            {"value": "CZC", "description": "郑商所期货"},
            {"value": "INE", "description": "上期能源期货"},
            {"value": "GFE", "description": "广期所期货"},
            {"value": "CFFO", "description": "中金所期权"},
            {"value": "CZCO", "description": "郑商所期权"},
            {"value": "DCEO", "description": "大商所期权"},
            {"value": "SHFO", "description": "上期所期权"},
            {"value": "GFEO", "description": "广期所期权"},
            {"value": "CSI", "description": "中证指数"},
            {"value": "CNI", "description": "国证指数"},
            {"value": "HG", "description": "恒生指数"},
            {"value": "HI", "description": "恒生综合指数"},
            {"value": "OF", "description": "开放式基金"},
        ],
        "valid_periods": [
            {"value": "tick", "description": "分时数据"},
            {"value": "5m", "description": "5分钟K线"},
            {"value": "10m", "description": "10分钟K线"},
            {"value": "15m", "description": "15分钟K线"},
            {"value": "30m", "description": "30分钟K线"},
            {"value": "1h", "description": "1小时K线"},
            {"value": "1d", "description": "日线"},
            {"value": "1w", "description": "周线"},
            {"value": "1mon", "description": "月线"},
            {"value": "1m", "description": "分钟线（同tick）"},
            {"value": "45d", "description": "45日线"},
            {"value": "1q", "description": "季线"},
            {"value": "1y", "description": "年线"},
        ],
        "valid_dividend_types": [
            {"value": "none", "description": "不复权"},
            {"value": "front", "description": "前复权"},
            {"value": "back", "description": "后复权"},
        ],
        "valid_report_types": [
            {"value": "report_time", "description": "报告期"},
            {"value": "publish_time", "description": "发布日期"},
            {"value": "announce_time", "description": "公告日期（同publish_time）"},
        ],
        "valid_formula_modes": [
            {"value": "zb", "description": "指标模式"},
            {"value": "xg", "description": "选股模式"},
            {"value": "exp", "description": "公式解释模式"},
            {"value": "raw", "description": "原始公式模式"},
        ],
        "valid_order_types": [
            {"value": 0, "description": "买入"},
            {"value": 1, "description": "卖出"},
            {"value": 69, "description": "买入（备用）"},
            {"value": 70, "description": "卖出（备用）"},
        ],
        "valid_price_types": [
            {"value": 0, "description": "最新价"},
            {"value": 1, "description": "买一价"},
            {"value": 2, "description": "卖一价"},
            {"value": 3, "description": "均价"},
        ],
        "valid_block_types": [
            {"value": 0, "description": "自定义板块"},
            {"value": 1, "description": "系统板块"},
            {"value": 2, "description": "指标板块"},
        ],
        "valid_list_types": [
            {"value": 0, "description": "全部A股"},
            {"value": 1, "description": "上证A股"},
            {"value": 5, "description": "深证A股"},
            {"value": 6, "description": "北证A股"},
            {"value": 7, "description": "科创板"},
            {"value": 8, "description": "创业板"},
            {"value": 9, "description": "中小板"},
            {"value": 10, "description": "三板"},
            {"value": 11, "description": "B股"},
            {"value": 12, "description": "基金"},
            {"value": 13, "description": "ETF"},
            {"value": 14, "description": "LOF"},
            {"value": 15, "description": "债券"},
            {"value": 16, "description": "可转债"},
            {"value": 17, "description": "指数"},
            {"value": 18, "description": "美股"},
            {"value": 21, "description": "港股"},
            {"value": 22, "description": "期货"},
            {"value": 23, "description": "期权"},
            {"value": 24, "description": "外汇"},
            {"value": 25, "description": "现货"},
            {"value": 26, "description": "自定义"},
            {"value": 27, "description": "主力合约"},
            {"value": 28, "description": "行业板块"},
            {"value": 30, "description": "地域板块"},
            {"value": 31, "description": "概念板块"},
            {"value": 32, "description": "风格板块"},
            {"value": 33, "description": "沪深300"},
            {"value": 34, "description": "上证50"},
            {"value": 35, "description": "中证500"},
            {"value": 36, "description": "创业板指"},
            {"value": 49, "description": "科创板指"},
            {"value": 50, "description": "北证50"},
            {"value": 51, "description": "科创50"},
            {"value": 52, "description": "科创100"},
            {"value": 53, "description": "创业板50"},
            {"value": 91, "description": "港股通沪"},
            {"value": 92, "description": "港股通深"},
            {"value": 101, "description": "存托凭证"},
            {"value": 102, "description": "CDR"},
            {"value": 103, "description": "其他"},
        ],
        "valid_markets": [
            {"value": "AG", "description": "A股市场"},
            {"value": "HK", "description": "港股市场"},
            {"value": "US", "description": "美股市场"},
        ],
        "valid_ipo_types": [
            {"value": 0, "description": "全部IPO"},
        ],
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

