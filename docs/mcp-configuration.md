# MCP 配置说明

本文说明如何将本仓库的 **TdxQuant MCP 服务** 接入各类 MCP 宿主（Cursor、Claude Desktop 等）。服务端实现基于 [FastMCP](https://github.com/jlowin/fastmcp)，支持 **stdio** 与 **HTTP/SSE** 两种传输方式。

## 传输方式选择

| 方式 | 入口模块 | 典型场景 |
|------|-----------|----------|
| **stdio** | `tdx_mcp.main_stdio` | Cursor、Claude Desktop 等通过子进程标准输入输出连接 |
| **HTTP/SSE** | `tdx_mcp.main_http` | 需单独启动进程，由支持 Streamable HTTP / SSE 的客户端连接 |

业务逻辑相同；stdio 无需配置 `MCP_HOST` / `MCP_PORT`，HTTP方式则必须配置并先启动服务进程。

---

## 环境变量（两种传输共用）

启动前请配置 `.env` 或系统环境变量（详见仓库根目录 [`.env.example`](../.env.example)）：

| 变量 | 必填 | 说明 |
|------|------|------|
| `TQ_PATH` | **是** | 通达信策略路径，与 `tqcenter` 初始化要求一致 |
| `TQ_DLL_PATH` | 否 | DLL 路径，多数情况留空 |
| `MCP_HOST` | 否 | 仅 **main_http**：监听地址，默认 `127.0.0.1` |
| `MCP_PORT` | 否 | 仅 **main_http**：监听端口，默认 `8765` |
| `MCP_BEARER_TOKEN` | 否 | 仅 **main_http**：Bearer 鉴权令牌；为空则不启用 |

**注意**：`main_stdio` 在内部仍会调用 `get_settings()`，**未设置 `TQ_PATH` 时进程会直接退出**。

---

## Cursor：stdio 配置

### 项目级（推荐）

在仓库根目录使用 Cursor **打开文件夹**，确保工作区根目录即包含 `tdx_mcp` 包与 `.env`。

已提供示例文件：[`.cursor/mcp.json`](../.cursor/mcp.json)

```json
{
  "mcpServers": {
    "tdxquant": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "tdx_mcp.main_stdio"],
      "envFile": "${workspaceFolder}/.env"
    }
  }
}
```

字段说明：

- **`mcpServers`**：服务器名称（此处 `tdxquant`）可自定义，在 Cursor MCP 列表中显示。
- **`type`**：`stdio` 表示通过命令启动子进程并用标准流通信。
- **`command`**：可执行文件，需在系统 PATH 中（如 `uv`、`python`）。
- **`args`**：传给 `command` 的参数数组。
- **`envFile`**：Cursor 支持的变量展开，`${workspaceFolder}` 为当前工作区根目录。也可改用 **`env`** 内联键值对。

修改配置后，在 **Cursor →设置 → MCP** 中刷新或重启 Cursor，查看该服务器是否变为已连接。

### 用户级（全局）

在用户目录下的 MCP 配置文件中添加同名结构（具体路径以 [Cursor 文档](https://cursor.com/docs/mcp) 为准，常见为 `~/.cursor/mcp.json`）。若使用 `envFile`，请改为**绝对路径**或确保 `cwd` 指向本仓库根目录。

### 无法找到 `uv` 时

将 `command` / `args` 改为虚拟环境中的 Python，例如（Windows，路径按本机修改）：

```json
{
  "mcpServers": {
    "tdxquant": {
      "type": "stdio",
      "command": "D:\\new_tdx_test\\PYPlugins\\user\\.venv\\Scripts\\python.exe",
      "args": ["-m", "tdx_mcp.main_stdio"],
      "env": {
        "TQ_PATH": "D:/path/to/your/strategy/script.py",
        "TQ_DLL_PATH": ""
      }
    }
  }
}
```

或在 `env` 中写入 `TQ_PATH`，不再依赖 `envFile`。

### 使用内联 `env` 替代 `envFile`

```json
"env": {
  "TQ_PATH": "D:/path/to/your/tdx/strategy/script.py",
  "TQ_DLL_PATH": ""
}
```

敏感信息勿提交到 Git；本地 `mcp.json` 若含密钥可加入 `.gitignore`。

---

## Claude Desktop：stdio 配置

编辑 Claude Desktop 的 MCP 配置文件（路径因系统而异，例如 Windows：`%APPDATA%\Claude\claude_desktop_config.json`），在 `mcpServers` 中增加一项：

```json
{
  "mcpServers": {
    "tdxquant": {
      "command": "uv",
      "args": ["run", "python", "-m", "tdx_mcp.main_stdio"],
      "env": {
        "TQ_PATH": "D:/path/to/your/tdx/strategy/script.py",
        "TQ_DLL_PATH": ""
      }
    }
  }
}
```

请将 `uv` 与 `python` 的工作目录设为本仓库根目录。若 `uv` 从任意目录运行，建议在 `args` 中使用 **`--directory`**（若 uv 版本支持）或改为 **Python 绝对路径 + `PYTHONPATH`** 指向项目根，确保 `tdx_mcp` 可被导入。

完整示例（指定工作目录，需根据 uv 版本调整）：

```json
{
  "mcpServers": {
    "tdxquant": {
      "command": "D:\\new_tdx_test\\PYPlugins\\user\\.venv\\Scripts\\python.exe",
      "args": ["-m", "tdx_mcp.main_stdio"],
      "cwd": "D:\\new_tdx_test\\PYPlugins\\user",
      "env": {
        "TQ_PATH": "D:/path/to/your/tdx/strategy/script.py"
      }
    }
  }
}
```

> `cwd` 是否被 Claude Desktop 传入子进程，以当前客户端版本文档为准；若不生效，请使用绝对路径的 Python 并设置 `PYTHONPATH`。

---

## HTTP / SSE（main_http）

1. 安装 HTTP 依赖：`uv sync --extra http`
2. 配置 `.env` 中的 `TQ_PATH`、`MCP_HOST`、`MCP_PORT`
3. 启动服务：

```bash
uv run python -m tdx_mcp.main_http
```

4. 在支持 **Streamable HTTP** 或 **SSE** 的 MCP 客户端中，按该客户端要求填写 **服务端 URL**（通常形如 `http://127.0.0.1:8765` 或文档给出的 MCP 路径，以 FastMCP / Cursor 当前版本为准）。

如已配置 `MCP_BEARER_TOKEN`，客户端请求需携带请求头：

```http
Authorization: Bearer <MCP_BEARER_TOKEN>
```

stdio 与 HTTP **不要对同一客户端重复配置为两个同名工具源**，按需选一种即可。

---

## 自检与排错

1. **命令行直接跑 stdio**（应阻塞等待输入，无立即报错即表示至少能导入并读到 `TQ_PATH`）：

   ```bash
   uv run python -m tdx_mcp.main_stdio
   ```

2. **查看 Cursor MCP 日志**：设置或帮助中打开 MCP 日志面板，确认子进程启动失败原因（PATH、`TQ_PATH`、导入错误等）。

3. **HTTP 自检**：浏览器或 `curl` 访问文档中给出的健康检查地址（若有）；否则以客户端连接成功为准。

4. **工具列表**：连接成功后，在对话中让模型先调用 **`tools_catalog`**，确认返回的分类与工具名称与 [README 工具示例](../README.md) 一致。需要平台背景说明时可调用 **`docs_get_tdxquant_intro`**（见 [TdxQuant 简介索引](tdxquant-intro.md)）。

---

## 参考链接

- [Cursor MCP 文档](https://cursor.com/docs/mcp)
- 仓库 [README.md](../README.md)：功能说明、工具调用示例、测试与故障排除
- [Agent 使用说明](agent-usage.md)：调用顺序、意图与工具对照、交易安全
- [TdxQuant 简介索引](tdxquant-intro.md)：官方帮助整理稿与 **`docs_get_tdxquant_intro`** 说明
- [Agent Skill 包](agent-skills.md)：SSE 场景下 Claude Code / OpenClaw / Hermes 的 Skill 与 MCP 片段
