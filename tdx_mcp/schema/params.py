from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable


SUPPORTED_STOCK_SUFFIXES = {
    "SZ",
    "SH",
    "BJ",
    "US",
    "HK",
    "NQ",
    "SZO",
    "SHO",
    "CSI",
    "CNI",
    "HG",
    "HI",
    "CFF",
    "SHF",
    "DCE",
    "CZC",
    "INE",
    "GFE",
    "CFFO",
    "CZCO",
    "DCEO",
    "SHFO",
    "GFEO",
    "OF",
}

VALID_PERIODS = {"tick", "5m", "15m", "30m", "1h", "1d", "1w", "1mon", "1m", "10m", "45d", "1q", "1y"}
VALID_DIVIDEND_TYPES = {"none", "front", "back"}
# announce_time 与 tdxdata_test /通达信侧「按公告日期」一致，与 publish_time 同义入参
VALID_REPORT_TYPES = {"report_time", "publish_time", "announce_time"}
VALID_FORMULA_MODES = {"zb", "xg", "exp", "raw"}
VALID_ORDER_TYPES = {0, 1, 69, 70}
VALID_PRICE_TYPES = {0, 1, 2, 3}
VALID_BLOCK_TYPES = {0, 1, 2}
# 来源 tdxdata_test.py（get_stock_list 注释），覆盖常见列表分类
VALID_LIST_TYPES = {
    0,
    1,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    49,
    50,
    51,
    52,
    53,
    91,
    92,
    101,
    102,
    103,
}
# 交易日历/缓存刷新常见市场口径
VALID_MARKETS = {"AG", "HK", "US"}
# get_ipo_info 的 ipo_type 口径以终端为准，当前先沉淀常用默认值
VALID_IPO_TYPES = {0}


def validate_symbol(symbol: str) -> str:
    if not isinstance(symbol, str):
        raise ValueError("symbol 必须是字符串")
    text = symbol.strip().upper()
    if "." not in text:
        raise ValueError(f"symbol 格式错误: {symbol}")
    code_part, suffix = text.rsplit(".", 1)
    if suffix not in SUPPORTED_STOCK_SUFFIXES:
        raise ValueError(f"不支持的代码后缀: {suffix}")
    if not code_part or not re.fullmatch(r"[0-9A-Za-z-]+", code_part):
        raise ValueError(f"symbol 主体格式错误: {symbol}")
    if suffix in {"SH", "SZ", "BJ"} and (not code_part.isdigit() or len(code_part) != 6):
        raise ValueError(f"A股/BJ 代码必须是6位数字: {symbol}")
    return text


def validate_symbol_list(symbols: Iterable[str]) -> list[str]:
    value = list(symbols)
    if not value:
        raise ValueError("stock_list 不能为空")
    return [validate_symbol(s) for s in value]


def validate_period(period: str) -> str:
    value = (period or "").strip().lower()
    if value not in VALID_PERIODS:
        raise ValueError(f"不支持的 period: {period}")
    return value


def validate_time_text(value: str | None) -> str:
    if not value:
        return ""
    text = value.strip()
    if re.fullmatch(r"\d{8}", text):
        datetime.strptime(text, "%Y%m%d")
        return text
    if re.fullmatch(r"\d{14}", text):
        datetime.strptime(text, "%Y%m%d%H%M%S")
        return text
    raise ValueError(f"时间格式错误: {value}，应为 YYYYMMDD 或 YYYYMMDDHHMMSS")


def validate_dividend_type(dividend_type: str | None) -> str:
    value = (dividend_type or "none").strip().lower()
    if value not in VALID_DIVIDEND_TYPES:
        raise ValueError(f"dividend_type 不支持: {dividend_type}")
    return value


def validate_report_type(report_type: str) -> str:
    value = (report_type or "report_time").strip().lower()
    if value not in VALID_REPORT_TYPES:
        raise ValueError(f"report_type 不支持: {report_type}")
    return value


def validate_formula_mode(mode: str) -> str:
    value = (mode or "raw").strip().lower()
    if value not in VALID_FORMULA_MODES:
        raise ValueError(f"formula mode 不支持: {mode}")
    return value

