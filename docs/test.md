# MCP 連線測試 — 指令與說明

測試 `paper-search`／`citation-verification-zh` 共用的兩個資料源 MCP server（`semantic-scholar` 與 `openalex`）是否可連線並實際查得到資料。安裝步驟另見 [`install.md`](install.md)。

## 執行指令

```bash
conda run -n research python tests/test_mcp_servers.py
```

- 全部通過會印出 `ALL PASS` 並以 exit code 0 結束；有任一項失敗印 `SOME CHECKS FAILED`、exit 1。
- 腳本只用 Python 標準函式庫（不需 `pymupdf` 等擷取套件），但因專案封鎖裸 `python`，仍透過 `conda run -n research` 執行。

## 測試內容

腳本讀取專案根目錄 `.mcp.json`，**照設定原樣啟動每個 server**，各跑三項檢查：

| # | 檢查 | 意義 |
|---|---|---|
| 1 | `initialize` 回傳 `serverInfo` | server 能啟動並正確講 MCP 協定 |
| 2 | `tools/list` 含預期工具 | Semantic Scholar 要有 `search_papers`；OpenAlex 要有 `search_works` |
| 3 | `tools/call` 實際搜尋回傳結果 | 帶憑證發一次真實查詢（query = `machine learning`），確認線上可用 |

憑證處理：`.mcp.json` 裡的 `${VAR:-}` 佔位會從 `.claude/settings.local.json` 的 `env` 展開後傳入子行程環境（Semantic Scholar 用 `SEMANTIC_SCHOLAR_API_KEY`；OpenAlex 用 `OPENALEX_EMAIL`／`OPENALEX_API_KEY`）。**金鑰只進子行程、不會被印出**；輸出僅顯示「哪些憑證有設」的布林狀態。

此測試**直接啟動 server**驗證，與 Claude Code session 內 `/mcp` 是否已掛載無關——不必先重啟 session 也能測。

## 預期輸出（範例）

```text
Paperdoku MCP connectivity test
config: .../Paperdoku/.mcp.json
------------------------------------------------------------
== semantic-scholar == (credentials set: SEMANTIC_SCHOLAR_API_KEY)
[PASS] semantic-scholar: initialize -> serverInfo 'semantic-scholar'
[PASS] semantic-scholar: tools/list has 'search_papers' (14 tools total)
[PASS] semantic-scholar: tools/call search_papers('machine learning') returned a result
------------------------------------------------------------
== openalex == (credentials set: OPENALEX_EMAIL, OPENALEX_API_KEY)
[PASS] openalex: initialize -> serverInfo 'openalex-mcp'
[PASS] openalex: tools/list has 'search_works' (31 tools total)
[PASS] openalex: tools/call search_works('machine learning') returned a result
------------------------------------------------------------
ALL PASS
```

## 疑難排解

- **`[FAIL] … no initialize/serverInfo response`**：前置工具缺失。`semantic-scholar` 需 `uv`／`uvx` 與 `git`；`openalex` 需 Node.js（`npx`）。見 [`install.md`](install.md)。首次執行 `uvx`／`npx` 會下載套件，較慢屬正常，腳本已放寬逾時。
- **`tools/call` 失敗但前兩項通過**：多半是網路或速率限制。OpenAlex 建議填 `OPENALEX_EMAIL`（polite pool）；Semantic Scholar 填 `SEMANTIC_SCHOLAR_API_KEY` 可提速。
- **`not found in .mcp.json`**：對應 server 未設定；檢查專案根目錄 `.mcp.json` 的 `mcpServers`。
