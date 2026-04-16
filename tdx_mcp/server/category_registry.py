from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolMeta:
    name: str
    category: str
    summary: str
    status: str = "implemented"


CATEGORY_DEFS: list[dict[str, str]] = [
    {"category": "连接管理", "description": "initialize/close_connection"},
    {"category": "行情数据", "description": "K线/Tick/除权"},
    {"category": "股票信息", "description": "详情/报价/盘口/估值/股本"},
    {"category": "板块数据", "description": "列表/成分股/自选/ETF"},
    {"category": "财务数据", "description": "财务报表/交易衍生数据"},
    {"category": "可转债/新股", "description": "CB信息/IPO信息"},
    {"category": "交易日历", "description": "按市场查询"},
    {"category": "交易接口", "description": "账户/持仓/委托/下单/撤单"},
    {"category": "工具/缓存", "description": "指标公式/板块操作/缓存刷新/平台简介文档"},
]


def build_catalog(tool_meta_list: list[ToolMeta]) -> dict[str, Any]:
    summary: list[dict[str, Any]] = []
    all_details: list[dict[str, str]] = []

    for category_def in CATEGORY_DEFS:
        category = category_def["category"]
        tools = [m for m in tool_meta_list if m.category == category]
        implemented = [m for m in tools if m.status == "implemented"]
        planned = [m for m in tools if m.status != "implemented"]
        summary.append(
            {
                "category": category,
                "tool_count": len(implemented),
                "implemented_count": len(implemented),
                "planned_count": len(planned),
                "description": category_def["description"],
                "tools": [m.name for m in implemented],
            }
        )
        all_details.extend(
            [
                {
                    "name": m.name,
                    "category": m.category,
                    "summary": m.summary,
                    "status": m.status,
                }
                for m in tools
            ]
        )

    return {
        "category_summary": summary,
        "tools": all_details,
    }

