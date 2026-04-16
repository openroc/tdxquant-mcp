# Agent Skill 包（TdxQuant MCP / SSE）

本仓库提供可复制的 **Skill 目录** [`skills/tdxquant-mcp/`](../skills/tdxquant-mcp/)，用于教会 **Claude Code**、**OpenClaw**、**Hermes Agent** 等：何时使用通达信量化 MCP、如何通过 **HTTP/SSE** 连接、推荐调用顺序与安全边界。

Skill 正文：`SKILL.md`（及 Hermes 常用的同名 **`skill.md`**，内容一致）。  
宿主专属 **JSON/YAML 配置片段**：[`skills/tdxquant-mcp/references/host-config-snippets.md`](../skills/tdxquant-mcp/references/host-config-snippets.md)。  
精简意图表：[`skills/tdxquant-mcp/references/workflow.md`](../skills/tdxquant-mcp/references/workflow.md)。

---

## 使用顺序（人类操作）

1. 配置 `.env`：`TQ_PATH` 必填；`MCP_HOST` / `MCP_PORT` 用于 HTTP 服务（默认 `127.0.0.1:8765`）。  
2. `uv sync --extra http`  
3. `uv run python -m tdx_mcp.main_http`（保持进程运行）  
4. 在目标 Agent 宿主中配置 MCP，**SSE URL** 为：`http://<MCP_HOST>:<MCP_PORT>/sse`  
5. （可选）将 Skill 目录安装到宿主识别的路径（见下文），便于按需加载说明。

通用 MCP 说明见 [mcp-configuration.md](mcp-configuration.md)；工具调用细节见 [agent-usage.md](agent-usage.md)。

---

## Claude Code

- **MCP**：使用 `type: "sse"` 与完整 URL（示例见 `host-config-snippets.md`）。官方说明以 [Claude Code MCP](https://docs.claude.com/en/docs/claude-code/mcp) 为准。  
- **Skills**：安装路径以当前 Anthropic / Claude Code 文档为准（常见为项目或用户目录下的 skills 文件夹）。将 **`skills/tdxquant-mcp/`** 整夹复制到该 skills 根目录下，保留子目录 `references/`。

---

## OpenClaw

- **MCP**：在 OpenClaw 配置的 `mcp.servers` 中注册 `url`指向 `http://.../sse`（默认传输为 SSE）。详见 [OpenClaw：mcp](https://docs.openclaw.ai/cli/mcp)。  
- **Skills**：将 **`skills/tdxquant-mcp/`** 复制到 `~/.openclaw/skills/` 或当前项目的 `skills/`（以你使用的 OpenClaw 版本说明为准）。

---

## Hermes Agent

- **MCP**：在 `~/.hermes/config.yaml` 的 `mcp_servers` 中配置 `url`；建议使用 `tools.include` 等过滤。详见 [Use MCP with Hermes](https://hermes-agent.nousresearch.com/docs/guides/use-mcp-with-hermes)。配置修改后使用 **`/reload-mcp`**。  
- **Skills**：将目录复制到 `~/.hermes/skills/<任意名称>/`，确保目录内包含 **`skill.md`**（本仓库已提供，与 `SKILL.md` 同内容）。

---

## 与 stdio 方式的关系

Cursor 等常用 **stdio** 子进程启动 `tdx_mcp.main_stdio`，无需单独 URL。  
本文 Skill 侧重 **HTTP/SSE**（`main_http`）；工具名称与工作流与 stdio **相同**。

---

## 相关链接

| 资源 | 说明 |
|------|------|
| [skills/tdxquant-mcp/SKILL.md](../skills/tdxquant-mcp/SKILL.md) | 技能主文档 |
| [host-config-snippets.md](../skills/tdxquant-mcp/references/host-config-snippets.md) | Claude Code / OpenClaw / Hermes 配置示例 |
| [TdxQuant 简介索引](tdxquant-intro.md) | 平台背景与 `docs_get_tdxquant_intro` |
