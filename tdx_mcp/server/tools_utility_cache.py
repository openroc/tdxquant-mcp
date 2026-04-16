from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.schema.params import validate_formula_mode
from tdx_mcp.service.tdx_service import TdxQuantService


def register_utility_cache_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="utility_formula_run")
    def utility_formula_run(
        formula_name: Annotated[str, Field(description="通达信公式名称（与终端中公式名一致）。")],
        formula_arg: Annotated[
            str,
            Field(description="公式参数字符串；多参数用英文逗号分隔，规则同终端公式调用。"),
        ] = "",
        mode: Annotated[
            str,
            Field(
                description="执行模式（大小写不敏感，须为之一）：zb（指标）、xg（选股）、exp（专家系统）、raw（原始 tdx_formula）。默认 raw。"
            ),
        ] = "raw",
        formula_type: Annotated[
            int,
            Field(description="仅 mode=raw 时有效：传给 tdx_formula 的公式类型整型，默认 0；其余模式忽略。"),
        ] = 0,
        xsflag: Annotated[
            int,
            Field(description="绘图/显示标志，zb/raw 等模式下常用，默认 -1；含义以通达信公式接口为准。"),
        ] = -1,
    ) -> dict:
        """工具/缓存：执行通达信公式，返回 meta（mode、耗时）与 data。"""
        mode_value = validate_formula_mode(mode)
        result = service.run_formula(
            formula_name=formula_name,
            formula_arg=formula_arg,
            mode=mode_value,
            formula_type=formula_type,
            xsflag=xsflag,
        )
        return {"meta": {"mode": mode_value, "elapsed_ms": result.elapsed_ms}, "data": result.data}

    @mcp.tool(name="formula_run")
    def formula_run_alias(
        formula_name: Annotated[str, Field(description="通达信公式名称。")],
        formula_arg: Annotated[str, Field(description="公式参数字符串，逗号分隔。")] = "",
        mode: Annotated[str, Field(description="zb / xg / exp / raw，见 utility_formula_run。")] = "raw",
        formula_type: Annotated[int, Field(description="raw 模式公式类型。")] = 0,
        xsflag: Annotated[int, Field(description="绘图标志。")] = -1,
    ) -> dict:
        """兼容别名：与 utility_formula_run 等价。"""
        return utility_formula_run(
            formula_name=formula_name,
            formula_arg=formula_arg,
            mode=mode,
            formula_type=formula_type,
            xsflag=xsflag,
        )

    @mcp.tool(name="utility_refresh_cache")
    def utility_refresh_cache(
        market: Annotated[
            str,
            Field(description="市场标识，如 AG（A股）、HK、US；对应 schema VALID_MARKETS，默认 AG。"),
        ] = "AG",
        force: Annotated[bool, Field(description="是否强制刷新本地/终端缓存。")] = False,
    ) -> dict:
        """工具/缓存：按市场刷新行情缓存。"""
        return service.refresh_cache(market=market, force=force)

    @mcp.tool(name="utility_refresh_kline")
    def utility_refresh_kline(
        stock_list: Annotated[list[str], Field(description="证券代码列表，格式同行情接口。")],
        period: Annotated[
            str,
            Field(description="刷新周期：本接口仅支持 1m、5m、1d（与 tqcenter.refresh_kline 限制一致）。"),
        ],
    ) -> dict:
        """工具/缓存：按代码列表与周期刷新 K 线缓存。"""
        return service.refresh_kline(stock_list=stock_list, period=period)

    @mcp.tool(name="utility_create_sector")
    def utility_create_sector(
        block_code: Annotated[str, Field(description="自定义板块简称/代码（终端内唯一）。")],
        block_name: Annotated[str, Field(description="自定义板块显示名称。")],
    ) -> dict:
        """工具/缓存：创建自定义板块。"""
        return service.create_sector(block_code=block_code, block_name=block_name)

    @mcp.tool(name="utility_delete_sector")
    def utility_delete_sector(block_code: Annotated[str, Field(description="要删除的自定义板块 block_code。")]) -> dict:
        """工具/缓存：删除自定义板块。"""
        return service.delete_sector(block_code=block_code)

    @mcp.tool(name="utility_rename_sector")
    def utility_rename_sector(
        block_code: Annotated[str, Field(description="已有自定义板块 block_code。")],
        block_name: Annotated[str, Field(description="新的板块显示名称。")],
    ) -> dict:
        """工具/缓存：重命名自定义板块。"""
        return service.rename_sector(block_code=block_code, block_name=block_name)

    @mcp.tool(name="utility_clear_sector")
    def utility_clear_sector(block_code: Annotated[str, Field(description="清空成分股的自定义板块 block_code。")]) -> dict:
        """工具/缓存：清空自定义板块。"""
        return service.clear_sector(block_code=block_code)

