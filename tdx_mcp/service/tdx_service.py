from __future__ import annotations

import atexit
import math
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd

from tqcenter import tq

from tdx_mcp.schema.params import (
    validate_dividend_type,
    validate_period,
    validate_report_type,
    validate_symbol,
    validate_symbol_list,
    validate_time_text,
)


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        frame = value.copy()
        if isinstance(frame.index, pd.DatetimeIndex):
            frame = frame.reset_index(names="datetime")
        frame = frame.where(pd.notna(frame), None)
        return frame.to_dict(orient="records")
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().isoformat(sep=" ")
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, dict):
        return {str(k): _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, float):
        return None if math.isnan(value) else value
    return value


@dataclass
class FormulaResult:
    data: dict[str, Any]
    elapsed_ms: int


class TdxQuantService:
    def __init__(self, tq_path: str, tq_dll_path: str = "") -> None:
        self._initialized = False
        self._tq_path = tq_path
        self._tq_dll_path = tq_dll_path

    def initialize(self) -> None:
        if self._initialized:
            return
        tq.initialize(path=self._tq_path, dll_path=self._tq_dll_path or "")
        atexit.register(self.close)
        self._initialized = True

    def close(self) -> None:
        if self._initialized:
            tq.close()
            self._initialized = False

    def initialize_connection(self) -> dict[str, Any]:
        self.initialize()
        return {"ok": True, "message": "连接已初始化"}

    def close_connection(self) -> dict[str, Any]:
        self.close()
        return {"ok": True, "message": "连接已关闭"}

    def _ensure_ready(self) -> None:
        if not self._initialized:
            self.initialize()

    def _reconnect(self) -> None:
        """Force reconnect TdxQuant session once for transient backend errors."""
        try:
            if self._initialized:
                tq.close()
        except Exception:
            pass
        tq.initialize(path=self._tq_path, dll_path=self._tq_dll_path or "")
        self._initialized = True

    @staticmethod
    def _is_empty_payload(data: Any) -> bool:
        if data is None:
            return True
        if isinstance(data, (dict, list, tuple, set, str)):
            return len(data) == 0
        return False

    @staticmethod
    def _filter_fields_case_insensitive(data: dict[str, Any], field_list: list[str] | None) -> dict[str, Any]:
        if not field_list:
            return data
        key_map = {k.lower(): k for k in data.keys()}
        selected: dict[str, Any] = {}
        for f in field_list:
            k = key_map.get(str(f).lower())
            if k is not None:
                selected[k] = data[k]
        return selected

    def get_market_snapshot(self, stock_code: str, field_list: list[str] | None = None) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        data = tq.get_market_snapshot(symbol, field_list or [])
        if self._is_empty_payload(data):
            self._reconnect()
            data = tq.get_market_snapshot(symbol, field_list or [])
        return _to_json_safe(data)

    def get_stock_info(self, stock_code: str, field_list: list[str] | None = None) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        data = tq.get_stock_info(symbol, field_list or [])
        if self._is_empty_payload(data):
            self._reconnect()
            data = tq.get_stock_info(symbol, field_list or [])
        return _to_json_safe(data)

    def get_market_data(
        self,
        stock_list: list[str],
        period: str,
        field_list: list[str] | None = None,
        start_time: str = "",
        end_time: str = "",
        count: int = -1,
        dividend_type: str | None = None,
        fill_data: bool = True,
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        period_value = validate_period(period)
        start_value = validate_time_text(start_time)
        end_value = validate_time_text(end_time)
        dividend_value = validate_dividend_type(dividend_type)

        # Do not pass field_list to tqcenter: it may print noisy false warnings
        # when payload is empty or field names vary by case.
        data = tq.get_market_data(
            stock_list=symbols,
            period=period_value,
            field_list=[],
            start_time=start_value,
            end_time=end_value,
            count=count,
            dividend_type=dividend_value,
            fill_data=fill_data,
        )
        if self._is_empty_payload(data):
            self._reconnect()
            data = tq.get_market_data(
                stock_list=symbols,
                period=period_value,
                field_list=[],
                start_time=start_value,
                end_time=end_value,
                count=count,
                dividend_type=dividend_value,
                fill_data=fill_data,
            )
        if isinstance(data, dict):
            data = self._filter_fields_case_insensitive(data, field_list)
        return _to_json_safe(data)

    def get_financial_data(
        self,
        stock_list: list[str],
        field_list: list[str] | None = None,
        start_time: str = "",
        end_time: str = "",
        report_type: str = "report_time",
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        report_value = validate_report_type(report_type)
        data = tq.get_financial_data(
            stock_list=symbols,
            field_list=field_list or [],
            start_time=validate_time_text(start_time),
            end_time=validate_time_text(end_time),
            report_type=report_value,
        )
        return _to_json_safe(data)

    def get_financial_data_by_date(
        self,
        stock_list: list[str],
        field_list: list[str] | None = None,
        year: int = 0,
        mmdd: int = 0,
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        data = tq.get_financial_data_by_date(
            stock_list=symbols,
            field_list=field_list or [],
            year=year,
            mmdd=mmdd,
        )
        return _to_json_safe(data)

    def list_sector(self, list_type: int = 0) -> list[dict[str, Any]]:
        self._ensure_ready()
        return _to_json_safe(tq.get_sector_list(list_type=list_type))

    def list_user_sector(self) -> list[dict[str, Any]]:
        self._ensure_ready()
        return _to_json_safe(tq.get_user_sector())

    def list_sector_stocks(self, block_code: str, block_type: int = 0, list_type: int = 0) -> list[dict[str, Any]]:
        self._ensure_ready()
        return _to_json_safe(
            tq.get_stock_list_in_sector(block_code=block_code, block_type=block_type, list_type=list_type)
        )

    def get_relation(self, stock_code: str) -> list[dict[str, Any]]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        return _to_json_safe(tq.get_relation(stock_code=symbol))

    def get_more_info(self, stock_code: str, field_list: list[str] | None = None) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        data = tq.get_more_info(stock_code=symbol, field_list=field_list or [])
        if self._is_empty_payload(data):
            self._reconnect()
            data = tq.get_more_info(stock_code=symbol, field_list=field_list or [])
        return _to_json_safe(data)

    def get_gb_info(self, stock_code: str, date_list: list[str], count: int = 1) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        return _to_json_safe(tq.get_gb_info(stock_code=symbol, date_list=date_list, count=count))

    def get_track_etf_info(self, zs_code: str) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe(tq.get_trackzs_etf_info(zs_code=zs_code))

    def get_kzz_info(self, stock_code: str, field_list: list[str] | None = None) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        return _to_json_safe(tq.get_kzz_info(stock_code=symbol, field_list=field_list or []))

    def get_ipo_info(self, ipo_type: int = 0, ipo_date: int = 0) -> list[dict[str, Any]]:
        self._ensure_ready()
        return _to_json_safe(tq.get_ipo_info(ipo_type=ipo_type, ipo_date=ipo_date))

    def get_trading_calendar(self, market: str, start_time: str, end_time: str) -> list[str]:
        self._ensure_ready()
        return _to_json_safe(
            tq.get_trading_calendar(
                market=market,
                start_time=validate_time_text(start_time),
                end_time=validate_time_text(end_time),
            )
        )

    def get_trading_dates(self, market: str, start_time: str, end_time: str, count: int = -1) -> list[str]:
        self._ensure_ready()
        return _to_json_safe(
            tq.get_trading_dates(
                market=market,
                start_time=validate_time_text(start_time),
                end_time=validate_time_text(end_time),
                count=count,
            )
        )

    def get_gpjy_value(
        self, stock_list: list[str], field_list: list[str] | None = None, start_time: str = "", end_time: str = ""
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        return _to_json_safe(
            tq.get_gpjy_value(
                stock_list=symbols,
                field_list=field_list or [],
                start_time=validate_time_text(start_time),
                end_time=validate_time_text(end_time),
            )
        )

    def get_bkjy_value(
        self, stock_list: list[str], field_list: list[str] | None = None, start_time: str = "", end_time: str = ""
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        return _to_json_safe(
            tq.get_bkjy_value(
                stock_list=symbols,
                field_list=field_list or [],
                start_time=validate_time_text(start_time),
                end_time=validate_time_text(end_time),
            )
        )

    def get_scjy_value(
        self, stock_list: list[str], field_list: list[str] | None = None, start_time: str = "", end_time: str = ""
    ) -> dict[str, Any]:
        self._ensure_ready()
        # 底层固定请求999999.SH，stock_list 仅用于与板块/个股类接口保持参数形态一致
        validate_symbol_list(stock_list)
        return _to_json_safe(
            tq.get_scjy_value(
                field_list=field_list or [],
                start_time=validate_time_text(start_time),
                end_time=validate_time_text(end_time),
            )
        )

    def subscribe_hq(self, stock_list: list[str]) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        # TdxQuant要求传入回调，MCP不处理实时回调，使用占位回调。
        result = tq.subscribe_hq(stock_list=symbols, callback=lambda _: None)
        return _to_json_safe({"result": result, "subscribed": symbols})

    def unsubscribe_hq(self, stock_list: list[str]) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        result = tq.unsubscribe_hq(stock_list=symbols)
        return _to_json_safe({"result": result, "unsubscribed": symbols})

    def get_subscribe_hq_stock_list(self) -> list[str]:
        self._ensure_ready()
        return _to_json_safe(tq.get_subscribe_hq_stock_list())

    def refresh_cache(self, market: str = "AG", force: bool = False) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe({"result": tq.refresh_cache(market=market, force=force)})

    def refresh_kline(self, stock_list: list[str], period: str) -> dict[str, Any]:
        self._ensure_ready()
        symbols = validate_symbol_list(stock_list)
        return _to_json_safe({"result": tq.refresh_kline(stock_list=symbols, period=period)})

    def create_sector(self, block_code: str, block_name: str) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe({"result": tq.create_sector(block_code=block_code, block_name=block_name)})

    def delete_sector(self, block_code: str) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe({"result": tq.delete_sector(block_code=block_code)})

    def rename_sector(self, block_code: str, block_name: str) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe({"result": tq.rename_sector(block_code=block_code, block_name=block_name)})

    def clear_sector(self, block_code: str) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe({"result": tq.clear_sector(block_code=block_code)})

    def get_account_id(self, account: str = "", account_type: str = "stock") -> int:
        self._ensure_ready()
        return int(tq.stock_account(account=account, account_type=account_type))

    def query_stock_asset(self, account_id: int) -> dict[str, Any]:
        self._ensure_ready()
        return _to_json_safe(tq.query_stock_asset(account_id=account_id))

    def query_stock_orders(self, account_id: int, stock_code: str = "", cancelable_only: bool = False) -> list[dict]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code) if stock_code else ""
        return _to_json_safe(tq.query_stock_orders(account_id=account_id, stock_code=symbol, cancelable_only=cancelable_only))

    def query_stock_positions(self, account_id: int) -> list[dict]:
        self._ensure_ready()
        return _to_json_safe(tq.query_stock_positions(account_id=account_id))

    def order_stock(
        self,
        account_id: int,
        stock_code: str,
        order_type: int,
        order_volume: int,
        price_type: int,
        price: float,
        notify: int = 0,
    ) -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code)
        return _to_json_safe(
            tq.order_stock(
                account_id=account_id,
                stock_code=symbol,
                order_type=order_type,
                order_volume=order_volume,
                price_type=price_type,
                price=price,
                notify=notify,
            )
        )

    def cancel_order_stock(self, account_id: int, order_id: str, stock_code: str = "") -> dict[str, Any]:
        self._ensure_ready()
        symbol = validate_symbol(stock_code) if stock_code else ""
        return _to_json_safe(tq.cancel_order_stock(account_id=account_id, stock_code=symbol, order_id=order_id))

    def run_formula(
        self,
        formula_name: str,
        formula_arg: str = "",
        mode: str = "raw",
        formula_type: int = 0,
        xsflag: int = -1,
    ) -> FormulaResult:
        self._ensure_ready()
        start = time.perf_counter()
        mode_value = (mode or "raw").strip().lower()
        if mode_value == "zb":
            data = tq.formula_zb(formula_name=formula_name, formula_arg=formula_arg, xsflag=xsflag)
        elif mode_value == "xg":
            data = tq.formula_xg(formula_name=formula_name, formula_arg=formula_arg)
        elif mode_value == "exp":
            data = tq.formula_exp(formula_name=formula_name, formula_arg=formula_arg)
        else:
            data = tq.tdx_formula(
                formula_type=formula_type,
                formula_name=formula_name,
                formula_arg=formula_arg,
                xsflag=xsflag,
            )
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return FormulaResult(data=_to_json_safe(data), elapsed_ms=elapsed_ms)

