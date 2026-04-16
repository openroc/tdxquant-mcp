# TdxQuant MCP 服务

基于本地 `tqcenter.py`（TdxQuant /通达信策略接口）的 **MCP（Model Context Protocol）** 封装。AI 客户端（如 Cursor）可通过 stdio 或 HTTP/SSE 调用工具，获取行情、财务、板块、公式等数据。

Python 包名：`tdxquant-mcp`（见 [`pyproject.toml`](pyproject.toml)）。

**MCP 接入**： [docs/mcp-configuration.md](docs/mcp-configuration.md)  
**Agent 使用（调用顺序、意图对照、交易安全）**： [docs/agent-usage.md](docs/agent-usage.md)  
**TdxQuant 平台简介（官方帮助整理 + MCP 工具说明）**： [docs/tdxquant-intro.md](docs/tdxquant-intro.md)  
**Agent Skill 包（Claude Code / OpenClaw / Hermes + SSE 配置）**： [docs/agent-skills.md](docs/agent-skills.md) · [`skills/tdxquant-mcp/`](skills/tdxquant-mcp/)

## Agent Skill 包

面向 **Claude Code**、**OpenClaw**、**Hermes Agent** 等：可复制目录 [`skills/tdxquant-mcp/`](skills/tdxquant-mcp/)（含 `SKILL.md` / `skill.md` 与 `references/` 下的 SSE 配置片段、精简工作流）。配合已启动的 **`tdx_mcp.main_http`**，客户端连接 **`http://<MCP_HOST>:<MCP_PORT>/sse`**。安装与宿主路径说明见 **[docs/agent-skills.md](docs/agent-skills.md)**。

## 功能概览

工具按业务分为 **9 类**（与 [`tools_catalog`](tdx_mcp/server/tools_catalog.py) / [`tool_metadata`](tdx_mcp/server/tool_metadata.py) 一致）：

| 分类 | 说明 |
|------|------|
| 连接管理 | 初始化 / 关闭通达信会话 |
| 行情数据 | K 线、Tick、快照、订阅 |
| 股票信息 | 基础资料、扩展信息、股本、跟踪指数 ETF |
| 板块数据 | 板块列表、成分股、自选板块、所属板块 |
| 财务数据 | 报表区间、报告日期、个股/板块/市场衍生 |
| 可转债/新股 | 可转债信息、新股申购 |
| 交易日历 | 交易日列表 |
| 交易接口 | 账户、资产、委托、持仓、下单/撤单（默认 dry-run） |
| 工具/缓存 | 公式执行、缓存刷新、自定义板块、**`docs_get_tdxquant_intro`**（平台简介 Markdown） |

**建议**：先调用工具 **`tools_catalog`**（无参数），返回分类与工具列表，再按需调用具体工具。  
**证券代码格式**：沪深等一般为 `600519.SH`、`000001.SZ`（大写市场后缀）。

---

## 仓库结构（与本项目相关）

```
user/
├── tqcenter.py              # TdxQuant Python 接口（依赖 TPythClient.dll 等）
├── tdxdata_test.py          # 直连 tq 的脚本示例（非 MCP）
├── skills/tdxquant-mcp/     # Agent Skill（SSE工作流 + 各宿主 MCP 片段）
├── tdx_mcp/                 # MCP 可安装包
│   ├── main_stdio.py        # stdio 入口（Cursor本地 MCP 推荐）
│   ├── main_http.py         # HTTP/SSE入口
│   ├── config.py            # 环境变量：TQ_PATH 等
│   ├── service/tdx_service.py
│   └── server/              # 各工具注册模块
├── tests/                   # pytest（含可选集成测试）
├── pyproject.toml
├── .env.example
├── docs/
│   ├── mcp-configuration.md # MCP 配置（Cursor / Claude / SSE）
│   ├── agent-usage.md       # Agent 使用说明（工作流、意图对照、交易）
│   ├── agent-skills.md      # Skill 包安装（Claude Code / OpenClaw / Hermes）
│   ├── tdxquant-intro.md    # TdxQuant 简介索引（正文见包内 resources）
│   └── mirror-tdx-quant-help/  # 运行 sync脚本后：官方帮助镜像 Markdown（可选）
└── .cursor/mcp.json         # Cursor 项目级 MCP 示例（可选）
```

---

## 运行前提

1. 本机可正常运行 **TdxQuant / 通达信** 终端（含策略能力），并已按官方说明配置策略路径。  
2. 项目目录下 **`tqcenter.py` 可被导入**（与 `TPythClient.dll` 等路径一致，见 TdxQuant 文档）。  
3. 已配置 **`TQ_PATH`**（指向策略脚本路径，与 `tq.initialize` 要求一致）。  
4. 推荐使用 [**uv**](https://github.com/astral-sh/uv) 管理依赖与运行命令。

---

## 安装

```bash
uv sync
```

HTTP/SSE 方式需要 ASGI 依赖：

```bash
uv sync --extra http
```

开发与测试：

```bash
uv sync --extra dev
```

**通达信量化在线帮助镜像**（爬取 `help.tdx.com.cn/quant/docs/` 下页面，生成本地 Markdown，可选）：

```bash
uv sync --extra sync-docs
python scripts/sync_tdx_help_docs.py
```

输出目录默认为 [`docs/mirror-tdx-quant-help/`](docs/mirror-tdx-quant-help/)（含 `pages/`、`_manifest.json`、`README.md`）。详见该目录内说明；正文版权归通达信，请以在线版为准。

---

## 环境变量

复制 [`.env.example`](.env.example) 为 `.env` 并修改：

| 变量 | 必填 | 说明 |
|------|------|------|
| `TQ_PATH` | 是 | 通达信策略连接路径（策略脚本所在路径，与 `tqcenter` 初始化一致） |
| `TQ_DLL_PATH` | 否 | DLL 路径，多数环境可留空 |
| `MCP_HOST` | 否 | HTTP/SSE 监听地址，默认 `127.0.0.1` |
| `MCP_PORT` | 否 | HTTP/SSE 监听端口，默认 `8765` |

MCP 进程启动时会加载 `get_settings()`，**缺少 `TQ_PATH` 会直接报错**。

---

## 在 Cursor 中配置 MCP（stdio）

项目内已提供示例 [`.cursor/mcp.json`](.cursor/mcp.json)（`uv` + `envFile`）。在 Cursor 中打开本仓库根目录后，于 **设置 → MCP** 中启用 **tdxquant**。

更完整的说明（含 Claude Desktop、`env` 内联、HTTP/SSE、排错）见 **[docs/mcp-configuration.md](docs/mcp-configuration.md)**。

---

## 启动方式

### stdio（推荐：Cursor、Claude Desktop 等）

```bash
uv run python -m tdx_mcp.main_stdio
```

### HTTP / SSE（独立进程，供支持远程 MCP 的客户端使用）

```bash
uv run python -m tdx_mcp.main_http
```

监听地址与端口由 **`MCP_HOST` / `MCP_PORT`** 决定（见 `.env`）。

---

## 工具名称与调用示例

下列名称与代码中 **`@mcp.tool(name="...")`** 完全一致。不同客户端里 JSON 字段可能为 `tool` / `name` / `toolName`，以你所用客户端文档为准。

### 获取工具目录

```json
{
  "tool": "tools_catalog",
  "arguments": {}
}
```

### 行情：最近 60 根日线

```json
{
  "tool": "market_get_kline",
  "arguments": {
    "stock_list": ["600519.SH"],
    "period": "1d",
    "count": 60,
    "dividend_type": "none"
  }
}
```

### 股票信息：扩展信息

```json
{
  "tool": "stock_get_more_info",
  "arguments": {
    "stock_code": "600519.SH"
  }
}
```

### 板块：成分股

```json
{
  "tool": "sector_stocks",
  "arguments": {
    "block_code": "BK0475",
    "block_type": 0,
    "list_type": 0
  }
}
```

### 财务：按报告期

```json
{
  "tool": "financial_get_report_by_date",
  "arguments": {
    "stock_list": ["600519.SH"],
    "year": 2024,
    "mmdd": 1231
  }
}
```

### 交易：下单预览（dry-run，默认）

实际下单需将 `dry_run` 设为 `false`，并自行承担风险；`account_id` 一般由 **`trade_get_account_id`** 取得。

```json
{
  "tool": "trade_order_stock",
  "arguments": {
    "account_id": 1001,
    "stock_code": "600519.SH",
    "order_type": 0,
    "order_volume": 100,
    "price_type": 0,
    "price": 1500.0,
    "dry_run": true
  }
}
```

### 工具：执行通达信公式

主入口为 **`utility_formula_run`**；另有别名 **`formula_run`**，行为相同。

```json
{
  "tool": "utility_formula_run",
  "arguments": {
    "formula_name": "KDJ",
    "formula_arg": "9,3,3",
    "mode": "zb"
  }
}
```

---

## 测试

### 单元测试（不连客户端）

```bash
uv run pytest tests/ -q
```

未设置联调环境变量时，集成用例会跳过，仅运行参数、目录等单元测试。

### 集成测试（需已登录通达信）

**CMD：**

```bat
set TDX_INTEGRATION=1
set TDX_STRICT_DATA=1
uv run pytest tests/test_tools_integration_tdxdata.py -m integration
```

**PowerShell：**

```powershell
$env:TDX_INTEGRATION = "1"
$env:TDX_STRICT_DATA = "1"
uv run pytest tests/test_tools_integration_tdxdata.py -m integration
```

- `TDX_STRICT_DATA`：可选，空数据时失败（默认允许空 dict 便于排查连接）。  
- `TDX_TRADE_ACCOUNT`：可选，交易类联调用账号字符串。

### 脚本示例（非 MCP）

[`tdxdata_test.py`](tdxdata_test.py) 演示直接调用 `tqcenter.tq`，用于对照接口行为；与 MCP 进程相互独立。

---

## 故障排除

| 现象 | 建议 |
|------|------|
| 启动报缺少 `TQ_PATH` | 检查 `.env` 或运行环境中的变量是否传入 MCP 子进程 |
| Cursor 无法启动 MCP | 见 [docs/mcp-configuration.md](docs/mcp-configuration.md) 排错；查看 MCP 日志，或改用虚拟环境 Python 绝对路径 |
| HTTP 无法连接 | 确认 `main_http` 已运行且防火墙放行 `MCP_HOST`:`MCP_PORT` |
| 数据为空 | 确认客户端已登录、盘后数据已下载；可适当关闭 `TDX_STRICT_DATA` 便于对比 |

---

## 许可证与上游

行为与数据格式以 **TdxQuant / 通达信** 与 `tqcenter.py` 为准；本仓库仅为 MCP 封装与文档整理。
