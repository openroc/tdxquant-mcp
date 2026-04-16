# Agent 使用说明

本文面向在 **Cursor Agent**、**Claude** 等环境中已通过 MCP 接入本服务的 AI 助手：说明如何稳定拉取通达信侧数据、如何组织调用顺序，以及**交易与合规**边界。

配置 MCP 本身（`mcp.json`、环境变量）见 [mcp-configuration.md](mcp-configuration.md)。工具名与 JSON 示例见仓库 [README.md](../README.md)。

---

## 使用前检查清单

在代表用户调用工具前，应理解以下前提（可向用户简短确认）：

1. **本机已打开并登录** TdxQuant / 通达信终端；部分数据需事先在客户端下载盘后数据。  
2. **MCP 已连接**：宿主设置中对应服务器（如 `tdxquant`）为已连接状态。  
3. **`TQ_PATH` 已正确配置**，否则服务进程无法完成 `tq` 初始化。  
4. 证券代码使用 **标准格式**：如 `600519.SH`、`000001.SZ`（**市场后缀大写**）。

---

## 推荐工作流（给 Agent 的执行顺序）

### 1. 先拉目录，再调具体工具

首次会话或不确定有哪些能力时，**优先调用**：

- **`tools_catalog`**（无参数）

若需要向用户解释 **TdxQuant 是什么、运行前提、tqcenter 能力**，可调用 **`docs_get_tdxquant_intro`**（无参数），使用返回的 `content`（Markdown）作为依据；原文链接见返回的 `source_url`。

从返回的 `category_summary` / `tools` 中确认工具**精确名称**（下划线风格，如 `market_get_kline`，不要用 `market.get_kline`）。

### 2. 按任务选工具（意图对照）

| 用户意图 | 常用工具 | 备注 |
|----------|-----------|------|
| K 线、Tick、历史行情 | `market_get_kline` | `period`：`1d` / `5m` / `tick` 等；`count` 与起止时间按接口说明 |
| 实时快照、五档等 | `market_get_snapshot` | 可能触发客户端刷新，耗时较长 |
| 股票名称、基础资料 | `stock_get_info` | |
| 更多字段、扩展信息 | `stock_get_more_info` | |
| 板块列表 | `sector_list` | |
| 板块成分股 | `sector_stocks` | 需正确 `block_code` / `block_type` |
| 财务区间 / 报告期 | `financial_get_report_range` / `financial_get_report_by_date` | 注意 `report_type`、年报 `mmdd` 如 `1231` |
| 可转债 / 新股 | `cbipo_get_kzz_info` / `cbipo_get_ipo_info` | |
| 交易日 | `calendar_get_trading_calendar` | |
| 通达信公式 | `utility_formula_run`或别名 `formula_run` | `mode`：`zb` / `xg` / `exp` / `raw` |
| 刷新缓存 | `utility_refresh_cache` / `utility_refresh_kline` | 谨慎高频调用 |
| TdxQuant 平台简介、运行环境 | `docs_get_tdxquant_intro` | 不依赖行情；返回 Markdown 正文与官方链接 |

连接异常时，用户可手动调用 **`connection_initialize`** / **`connection_close`**；多数场景下服务启动时已初始化。

### 3. 处理返回结果

- 返回可能是 **JSON 可序列化结构**（列表、字典）；K 线等可能为「按标的分组的字典」或记录列表，以实际返回为准。  
- **空字典 / 空列表**：可能是未登录、未下载数据、代码错误、或临时接口失败；应结合用户终端状态说明，避免编造数值。  
- **不要在缺少工具返回的情况下** 捏造行情或财务数字。

---

## 示例：用户自然语言 → Agent 行为

以下仅示意 Agent 内部应触发的工具链，实际参数需按用户补充。

**用户**：「查一下贵州茅台最近 60 天日线，不复权。」

1. 调用 `market_get_kline`，`stock_list`: `["600519.SH"]`，`period`: `"1d"`，`count`: `60`，`dividend_type`: `"none"`。  
2. 将结果整理为表格或要点；若为空，提示检查客户端与数据下载。

**用户**：「沪深 300 里有哪些股票？」（需用户或 Agent 先解析出板块/指数代码）

1. 可能需要 `sector_list` 或用户直接给出 `block_code`。  
2. 调用 `sector_stocks` 传入正确 `block_code` 与 `block_type`。

**用户**：「用指标公式算一下 KDJ(9,3,3)。」

1. 调用 `utility_formula_run`，`formula_name`: `"KDJ"`，`formula_arg`: `"9,3,3"`，`mode`: `"zb"`（若公式为指标类）。  
2. 若报错，尝试 `mode` 或公式名是否与客户端一致。

---

## 交易类工具（高风险）

涉及 **`trade_order_stock`**、**`trade_cancel_order_stock`**、**`trade_query_*`** 等时：

- **默认 `dry_run=true`**：仅返回预览 payload，**未真实下单**。  
- 仅在用户**明确授权**且理解后果时，才应在参数中使用 `dry_run=false`；Agent 应再次确认，**不得替用户默认关闭 dry-run**。  
- `account_id` 通常需先通过 **`trade_get_account_id`**（及用户提供的账号信息）取得。  
- **本服务不提供投资建议**；任何下单决策由用户自行负责。

---

## 常见失败原因（便于 Agent 向用户解释）

| 现象 | 可能原因 |
|------|-----------|
| MCP 无法连接 | 未配置或错误配置 `mcp.json` /环境变量；见 [mcp-configuration.md](mcp-configuration.md) |
| 工具报错或立即退出 | `TQ_PATH` 缺失或路径错误 |
| 数据一直为空 | 客户端未登录、未下载对应周期数据、代码格式错误 |
| 快照/全市场类很慢 | 接口会触发客户端刷新，属预期行为 |

---

## 与「读代码」分工

- **MCP 工具**：适合拉取终端侧实时/准实时数据、跑公式、查板块财务等。  
- **仓库内 `tqcenter.py` / `tdxdata_test.py`**：适合人类或 Agent **查接口语义、字段含义**；若需确认参数细节，可结合阅读 `tdx_mcp/schema/params.py` 与 `tdx_mcp/service/tdx_service.py`。

---

## 相关文档

| 文档 | 内容 |
|------|------|
| [mcp-configuration.md](mcp-configuration.md) | MCP 安装与 Cursor / Claude / HTTP 配置 |
| [README.md](../README.md) | 项目简介、环境变量、工具 JSON 示例、测试 |
