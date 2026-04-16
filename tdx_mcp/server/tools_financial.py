from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_financial_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="financial_get_report_range")
    def financial_get_report_range(
        stock_list: Annotated[
            list[str],
            Field(description='证券代码列表，格式同行情接口（如 "600519.SH"），须通过 validate_symbol_list。'),
        ],
        field_list: Annotated[
            list[str] | None,
            Field(
                description="财报指标字段名列表；留空由通达信返回默认列。字段名需与终端/文档一致（区分大小写以 tqcenter 为准）。"
            ),
        ] = None,
        start_time: Annotated[str, Field(description="报告区间起始：YYYYMMDD 或 YYYYMMDDHHMMSS；可空表示不限制。")] = "",
        end_time: Annotated[str, Field(description="报告区间结束：YYYYMMDD 或 YYYYMMDDHHMMSS；可空表示不限制。")] = "",
        report_type: Annotated[
            str,
            Field(
                description="报告期口径，须为之一（大小写不敏感）：report_time（报告期截止日）、publish_time / announce_time（按公告日期，二者等价）。默认 report_time。"
            ),
        ] = "report_time",
    ) -> dict:
        """财务数据：按时间范围查询财务报表（tqcenter.get_financial_data）。"""
        return service.get_financial_data(
            stock_list=stock_list,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
            report_type=report_type,
        )

    @mcp.tool(name="financial_get_report_by_date")
    def financial_get_report_by_date(
        stock_list: Annotated[list[str], Field(description="证券代码列表，格式同 financial_get_report_range。")],
        field_list: Annotated[
            list[str] | None,
            Field(description="财务指标字段名；留空返回默认列。"),
        ] = None,
        year: Annotated[int, Field(description="报告年份，如 2025；与 mmdd 一起指定报告期（如年报 2025+1231）。")] = 0,
        mmdd: Annotated[int, Field(description="报告期月日 MMDD（整数），如 0331 一季报、0630 半年报、1231 年报。")] = 0,
    ) -> dict:
        """财务数据：按指定报告期（年+MMDD）查询财务报表。"""
        return service.get_financial_data_by_date(stock_list=stock_list, field_list=field_list, year=year, mmdd=mmdd)

    @mcp.tool(name="financial_get_gpjy")
    def financial_get_gpjy(
        stock_list: Annotated[list[str], Field(description="股票代码列表（个股），格式如 600519.SH。")],
        field_list: Annotated[
            list[str] | None,
            Field(description="衍生指标字段名；留空返回默认列。"),
        ] = None,
        start_time: Annotated[str, Field(description="起始时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
        end_time: Annotated[str, Field(description="结束时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
    ) -> dict:
        """财务数据：股票交易衍生数据（get_gpjy_value）。"""
        return service.get_gpjy_value(stock_list=stock_list, field_list=field_list, start_time=start_time, end_time=end_time)

    @mcp.tool(name="financial_get_bkjy")
    def financial_get_bkjy(
        stock_list: Annotated[
            list[str],
            Field(description="板块代码列表（与个股接口相同参数形态，每项须通过 validate_symbol；实际为板块侧代码，参见终端板块代码）。"),
        ],
        field_list: Annotated[list[str] | None, Field(description="衍生指标字段名；留空返回默认列。")] = None,
        start_time: Annotated[str, Field(description="起始时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
        end_time: Annotated[str, Field(description="结束时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
    ) -> dict:
        """财务数据：板块交易衍生数据（get_bkjy_value）。"""
        return service.get_bkjy_value(stock_list=stock_list, field_list=field_list, start_time=start_time, end_time=end_time)

    @mcp.tool(name="financial_get_scjy")
    def financial_get_scjy(
        stock_list: Annotated[
            list[str],
            Field(
                description='须非空且每项通过 validate_symbol（如 ["600519.SH"]）；底层 tq.get_scjy_value 固定请求全市场口径，本参数仅与个股/板块类接口保持形态一致，不改变实际查询范围。'
            ),
        ],
        field_list: Annotated[list[str] | None, Field(description="市场衍生指标字段名；留空返回默认列。")] = None,
        start_time: Annotated[str, Field(description="起始时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
        end_time: Annotated[str, Field(description="结束时间 YYYYMMDD 或 YYYYMMDDHHMMSS。")] = "",
    ) -> dict:
        """财务数据：市场交易衍生数据（get_scjy_value）；stock_list 仅校验形态，实际请求由终端固定。"""
        return service.get_scjy_value(stock_list=stock_list, field_list=field_list, start_time=start_time, end_time=end_time)

