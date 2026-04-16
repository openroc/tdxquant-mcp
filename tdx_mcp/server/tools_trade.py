from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

from tdx_mcp.service.tdx_service import TdxQuantService


def register_trade_tools(mcp: FastMCP, service: TdxQuantService) -> None:
    @mcp.tool(name="trade_get_account_id")
    def trade_get_account_id(
        account: Annotated[str, Field(description="交易账号标识（与通达信终端中资金账号/配置一致）。")],
        account_type: Annotated[
            str,
            Field(description="账号类型字符串，默认 \"stock\"；期货等场景以终端与 tqcenter 约定为准。"),
        ] = "stock",
    ) -> dict:
        """交易接口：解析账号得到 account_id（整数句柄），供后续 query/order 使用。"""
        account_id = service.get_account_id(account=account, account_type=account_type)
        return {"account_id": account_id}

    @mcp.tool(name="trade_query_asset")
    def trade_query_asset(
        account_id: Annotated[int, Field(description="由 trade_get_account_id 返回的 account_id（整数句柄）。")]
    ) -> dict:
        """交易接口：查询账户资金与资产汇总。"""
        return service.query_stock_asset(account_id=account_id)

    @mcp.tool(name="trade_query_orders")
    def trade_query_orders(
        account_id: Annotated[int, Field(description="账户句柄 account_id。")],
        stock_code: Annotated[
            str,
            Field(description='可选；非空时仅筛选该证券（如 "600519.SH"），空字符串表示全部。'),
        ] = "",
        cancelable_only: Annotated[bool, Field(description="为 true 时仅返回当前可撤委托。")] = False,
    ) -> list[dict]:
        """交易接口：查询当日委托列表。"""
        return service.query_stock_orders(account_id=account_id, stock_code=stock_code, cancelable_only=cancelable_only)

    @mcp.tool(name="trade_query_positions")
    def trade_query_positions(
        account_id: Annotated[int, Field(description="账户句柄 account_id。")]
    ) -> list[dict]:
        """交易接口：查询当前持仓。"""
        return service.query_stock_positions(account_id=account_id)

    @mcp.tool(name="trade_order_stock")
    def trade_order_stock(
        account_id: Annotated[int, Field(description="账户句柄 account_id。")],
        stock_code: Annotated[str, Field(description='证券代码，如 "600519.SH"。')],
        order_type: Annotated[
            int,
            Field(
                description=(
                    "委托类型（整型，与 tqconst 一致，参见 TdxQuant 文档）："
                    "普通买入 STOCK_BUY=0，卖出 STOCK_SELL=1；"
                    "担保品买入/卖出与0/1 同号；"
                    "融资买入 CREDIT_FIN_BUY=69，融券卖出 CREDIT_SLO_SELL=70。"
                    "当前 schema 常量 VALID_ORDER_TYPES={0,1,69,70}。"
                )
            ),
        ],
        order_volume: Annotated[int, Field(description="委托数量（股），须满足交易单位与限额规则。")],
        price_type: Annotated[
            int,
            Field(
                description=(
                    "报价类型：PRICE_MY=0 自填价格（使用 price 参数）；"
                    "PRICE_SJ=1 市价；PRICE_ZTJ=2 涨停价；PRICE_DTJ=3 跌停价。"
                    "price_type 为市价时，具体市价模式依赖客户端「系统设置-参数」；其余以通达信为准。"
                    "当前 schema 常量 VALID_PRICE_TYPES={0,1,2,3}。"
                )
            ),
        ],
        price: Annotated[
            float,
            Field(description="委托价格；price_type=0时生效，市价等类型下含义以终端为准。"),
        ],
        notify: Annotated[int, Field(description="通知/回调标记，默认 0；含义以 tqcenter.order_stock 为准。")] = 0,
        dry_run: Annotated[
            bool,
            Field(description="默认 true：仅返回拟提交参数，不调用实盘下单；false 时真实报单，请谨慎。"),
        ] = True,
    ) -> dict:
        """交易接口：股票下单。默认 dry_run 预览；实盘前务必确认参数与风险。"""
        payload = {
            "account_id": account_id,
            "stock_code": stock_code,
            "order_type": order_type,
            "order_volume": order_volume,
            "price_type": price_type,
            "price": price,
            "notify": notify,
        }
        if dry_run:
            return {"dry_run": True, "payload": payload, "message": "仅预览参数，未实际下单"}
        return service.order_stock(**payload)

    @mcp.tool(name="trade_cancel_order_stock")
    def trade_cancel_order_stock(
        account_id: Annotated[int, Field(description="账户句柄 account_id。")],
        order_id: Annotated[str, Field(description="待撤委托单号（与 query_orders 返回一致）。")],
        stock_code: Annotated[str, Field(description='可选证券代码，如 "600519.SH"；无则传空字符串。')] = "",
        dry_run: Annotated[bool, Field(description="默认 true 仅预览；false 执行实盘撤单。")] = True,
    ) -> dict:
        """交易接口：股票撤单；默认 dry_run。"""
        payload = {"account_id": account_id, "order_id": order_id, "stock_code": stock_code}
        if dry_run:
            return {"dry_run": True, "payload": payload, "message": "仅预览参数，未实际撤单"}
        return service.cancel_order_stock(**payload)

