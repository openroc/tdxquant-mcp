# TdxQuant 简介（文档副本说明）

- **官方页面**：[TdxQuant 简介 | 通达信量化平台](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/)
- **MCP 工具**：调用 **`docs_get_tdxquant_intro`**（无参数）可返回 `title`、`source_url` 与完整 **`content`**（Markdown字符串），供 Agent 直接阅读。
- **仓库内正文源文件**（与工具返回一致）：[`tdx_mcp/resources/tdxquant_intro.md`](../tdx_mcp/resources/tdxquant_intro.md)

## 完整在线帮助镜像（本地 Markdown）

从官方 `help.tdx.com.cn/quant/docs/` 子站爬取整理的**多页**副本位于 **[`mirror-tdx-quant-help/`](mirror-tdx-quant-help/README.md)**：

- 总目录与版权声明：[`mirror-tdx-quant-help/README.md`](mirror-tdx-quant-help/README.md)
- 页面正文：`mirror-tdx-quant-help/pages/*.md`
- 抓取清单：[`mirror-tdx-quant-help/_manifest.json`](mirror-tdx-quant-help/_manifest.json)

更新方式：安装可选依赖 `sync-docs` 后执行 `python scripts/sync_tdx_help_docs.py`（见根目录 [README.md](../README.md)）。**请以官方在线版为准**。

---

若仅需简介、不需全量镜像，在 IDE 中可直接打开 [`tdx_mcp/resources/tdxquant_intro.md`](../tdx_mcp/resources/tdxquant_intro.md)。
