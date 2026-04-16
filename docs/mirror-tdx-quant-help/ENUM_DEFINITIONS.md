# 枚举定义对照表（文档 vs Schema）

本文用于统一 `docs/mirror-tdx-quant-help` 镜像文档与 `tdx_mcp/schema/params.py` 的参数枚举口径，便于工具接口说明、校验与兼容处理。

## 1. 证券后缀（symbol suffix）

### 文档来源
- `pages/markdown__Dict.html.md`

### 对照结果
| 项目 | 文档枚举 | Schema 枚举 | 结论 |
|---|---|---|---|
| 证券后缀 | `.SZ .SH .BJ .NQ .SHO .SZO .HK .US .CSI .CNI .HG .CFF .CZC .DCE .SHF .GFE .INE .HI .OF .CFFO .CZCO .DCEO .SHFO .GFEO` | `SZ SH BJ NQ SHO SZO HK US CSI CNI HG CFF CZC DCE SHF GFE INE HI OF CFFO CZCO DCEO SHFO GFEO` | 一致（文档带前导点，Schema 不带点） |

---

## 2. 复权类型（dividend_type）

### 文档来源
- `pages/markdown__Dict.html.md`
- `pages/markdown__mindoc-1ctuhthaq5qmg__mindoc-1h10g60jt68sc.html.md`
- 旧公式相关页（存在整数写法）

### 对照结果
| 项目 | 文档枚举 | Schema 枚举 | 结论 |
|---|---|---|---|
| dividend_type | `none` / `front` / `back` | `none` / `front` / `back` | 一致 |
| 旧接口写法 | `0不复权 1前复权 2后复权` | 无（Schema 仅字符串） | 建议在服务层做兼容映射 |

### 建议映射
| 旧值 | 新值 |
|---|---|
| `0` | `none` |
| `1` | `front` |
| `2` | `back` |

---

## 3. K线周期（period）

### 文档来源
- `pages/markdown__Dict.html.md`

### 对照结果
| 分类 | 枚举值 |
|---|---|
| 文档标准集 | `tick, 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon, 1q, 1y` |
| Schema 集（`VALID_PERIODS`） | `tick, 1m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1mon, 45d, 1q, 1y` |
| 差异项 | `10m, 45d`（Schema 有，镜像 Dict 页未列出） |

### 建议
- 对外文档可声明“标准周期 + 扩展周期（以当前 Schema/终端能力为准）”。

---

## 4. 报表时间口径（report_type）

### 文档来源
- `pages/markdown__TdxQuant.md__mindoc-1h10m001ic888.html.md`

### 对照结果
| 口径 | 文档写法 | Schema 写法（`VALID_REPORT_TYPES`） | 备注 |
|---|---|---|---|
| 公告日期 | `announce_time` | `announce_time` | 一致 |
| 报告期日期 | `tag_time` | `report_time` | 命名差异（历史文档用 `tag_time`） |
| 发布日期 | 未明确列出 | `publish_time` | Schema 扩展/兼容口径 |

### 兼容建议
- 在接口说明中明确：
  - `announce_time`：按公告日期；
  - `report_time`：按报告期（兼容文档中的 `tag_time`）；
  - `publish_time`：保留兼容值。

---

## 5. 下单委托类型（order_type）

### 文档来源
- `pages/markdown__Dict.html.md`
- `pages/markdown__mindoc-1h7k4iqb1grk4__mindoc-1h7k5j4drr928.html.md`

### 对照结果
| 常量名 | 数值 | 说明 |
|---|---:|---|
| `STOCK_BUY` | 0 | 买入 |
| `STOCK_SELL` | 1 | 卖出 |
| `CREDIT_BUY` | 0 | 担保品买入 |
| `CREDIT_SELL` | 1 | 担保品卖出 |
| `CREDIT_FIN_BUY` | 69 | 融资买入 |
| `CREDIT_SLO_SELL` | 70 | 融券卖出 |

---

## 6. 报价类型（price_type）

### 文档来源
- `pages/markdown__Dict.html.md`
- `pages/markdown__mindoc-1h7k4iqb1grk4__mindoc-1h7k5j4drr928.html.md`

### 对照结果
| 常量名 | 数值 | 说明 |
|---|---:|---|
| `PRICE_MY` | 0 | 自填价 |
| `PRICE_SJ` | 1 | 市价 |
| `PRICE_ZTJ` | 2 | 涨停价/笼子上限 |
| `PRICE_DTJ` | 3 | 跌停价/笼子下限 |

### 备注
- 当 `price_type=1`（市价）时，具体市价子类型受客户端参数设置影响。

---

## 7. 委托状态（可选补充）

### 文档来源
- `pages/markdown__Dict.html.md`

### 文档枚举
| 常量名 | 数值 | 说明 |
|---|---:|---|
| `WTSTATUS_NULL` | 0 | 无效单 |
| `WTSTATUS_NOCJ` | 1 | 未成交 |
| `WTSTATUS_PARTCJ` | 2 | 部分成交 |
| `WTSTATUS_ALLCJ` | 3 | 全部成交 |
| `WTSTATUS_BCBC` | 4 | 部分成交部分撤单 |
| `WTSTATUS_ALLCD` | 5 | 全部撤单 |

> 当前 `schema/params.py` 未定义该组常量；若后续有状态参数校验需求，可新增为 `VALID_ORDER_STATUS`。

---

## 8. 公式模式（mode）

### 文档来源
- `pages/markdown__mindoc-1h3hrvkp4sc0g__mindoc-1h3huq37005ro.html.md`（`formula_zb/xg/exp`）

### 对照结果
| 项目 | 文档体现 | Schema 枚举（`VALID_FORMULA_MODES`） | 结论 |
|---|---|---|---|
| 公式模式 | `zb, xg, exp` | `zb, xg, exp, raw` | `raw` 为 MCP 封装扩展 |

### 备注
- `raw` 模式对应底层 `tdx_formula` 直调能力，不冲突于文档现有三种快捷模式。

---

## 9. 统一口径建议（用于接口文案）

1. **枚举展示优先级**：先按镜像文档列值，再补充 Schema 扩展项。  
2. **命名兼容**：对 `tag_time/report_time`、`0/1/2` 复权值等历史写法，在说明中给出映射，不直接删除兼容语义。  
3. **工具化输出**：`tools_enum_definitions` 建议返回：
   - `supported_stock_suffixes`
   - `valid_periods`
   - `valid_dividend_types`
   - `valid_report_types`
   - `valid_formula_modes`
4. **避免歧义**：对于“以终端设置为准”的参数（如市价子类型），在字段说明中明确标注运行时依赖。

---

## 10. 股票列表类型（list_type）

来源：`tdxdata_test.py`（示例注释，`get_stock_list` 相关）。

| list_type | 含义 |
|---:|---|
| 0 | 自选股 |
| 1 | 持仓股 |
| 5 | 所有A股 |
| 6 | 上证指数成份股 |
| 7 | 上证主板 |
| 8 | 深证主板 |
| 9 | 重点指数 |
| 10 | 所有板块指数 |
| 11 | 缺省行业板块 |
| 12 | 概念板块 |
| 13 | 风格板块 |
| 14 | 地区板块 |
| 15 | 缺省行业分类+概念板块 |
| 16 | 研究行业一级 |
| 17 | 研究行业二级 |
| 18 | 研究行业三级 |
| 21 | 含H股 |
| 22 | 含可转债 |
| 23 | 沪深300 |
| 24 | 中证500 |
| 25 | 中证1000 |
| 26 | 国证2000 |
| 27 | 中证2000 |
| 28 | 中证A500 |
| 30 | REITs |
| 31 | ETF基金 |
| 32 | 可转债 |
| 33 | LOF基金 |
| 34 | 所有可交易基金 |
| 35 | 所有沪深基金 |
| 36 | T+0基金 |
| 49 | 金融类企业 |
| 50 | 沪深A股 |
| 51 | 创业板 |
| 52 | 科创板 |
| 53 | 北交所 |
| 91 | ETF追踪的指数 |
| 92 | 国内期货主力合约 |
| 101 | 国内期货 |
| 102 | 港股 |
| 103 | 美股 |

备注：
- 该表来自本仓库测试脚本注释，属于实务侧枚举补充；
- 若与终端版本不一致，请以通达信客户端实际返回为准。

