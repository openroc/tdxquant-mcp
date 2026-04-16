from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.schema.params import validate_formula_mode
from tdx_mcp.service.tdx_service import TdxQuantService


def register_formula_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="formula.run")
    def formula_run(
        formula_name: Annotated[str, Field(description="通达信公式名称（与终端一致）。")],
        formula_arg: Annotated[str, Field(description="公式参数，多参数英文逗号分隔。")] = "",
        mode: Annotated[
            str,
            Field(description="zb（指标）/ xg（选股）/ exp（专家系统）/ raw；须符合 schema VALID_FORMULA_MODES。"),
        ] = "raw",
        formula_type: Annotated[int, Field(description="mode=raw 时传入 tdx_formula 的类型整型。")] = 0,
        xsflag: Annotated[int, Field(description="绘图标志，默认 -1。")] = -1,
    ) -> dict:
        """
        执行通达信公式并返回 meta（formula_name、mode、elapsed_ms）与 data。
        mode为 zb/xg/exp 时走快捷封装；mode=raw 时使用 tdx_formula，并传入 formula_type、xsflag。
        与 utility_formula_run 逻辑等价，仅返回 meta 字段略多。
        """
        mode_value = validate_formula_mode(mode)
        result = service.run_formula(
            formula_name=formula_name,
            formula_arg=formula_arg,
            mode=mode_value,
            formula_type=formula_type,
            xsflag=xsflag,
        )
        return {
            "meta": {
                "formula_name": formula_name,
                "mode": mode_value,
                "elapsed_ms": result.elapsed_ms,
            },
            "data": result.data,
        }

