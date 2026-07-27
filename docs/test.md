# 測試 — 指令與說明

Paperdoku 的三組自測。全部不依賴 pytest，通過印 `ALL PASS`、以 exit code 0 結束。安裝步驟另見 [`install.md`](install.md)。

| 組別 | 指令 | 何時該跑 |
|---|---|---|
| MCP 連線 | `tests/test_mcp_servers.py` | 裝好／改過 `.mcp.json` 或憑證後 |
| 擷取層 | `.claude/skills/source-document-extraction/tests/*.py` | 改過擷取或清理腳本後 |
| Skill frontmatter | `tests/test_skill_frontmatter.py` | **改過任何 `SKILL.md` frontmatter 後（必跑）** |

## 1. MCP 連線測試

測試 `paper-search`／`citation-verification-zh` 共用的兩個資料源 MCP server（`semantic-scholar` 與 `openalex`）是否可連線並實際查得到資料。

### 執行指令

可**自己在終端機執行**，或直接**請 Claude 代為執行**（開著 Claude Code 時說「幫我跑 MCP 連線測試」即可）：

```bash
conda run -n research python tests/test_mcp_servers.py
```

- 全部通過會印出 `ALL PASS` 並以 exit code 0 結束；有任一項失敗印 `SOME CHECKS FAILED`、exit 1。
- 腳本只用 Python 標準函式庫（不需 `pymupdf` 等擷取套件），但因專案封鎖裸 `python`，仍透過 `conda run -n research` 執行。

### 測試內容

腳本讀取專案根目錄 `.mcp.json`，**照設定原樣啟動每個 server**，各跑三項檢查：

| # | 檢查 | 意義 |
|---|---|---|
| 1 | `initialize` 回傳 `serverInfo` | server 能啟動並正確講 MCP 協定 |
| 2 | `tools/list` 含預期工具 | Semantic Scholar 要有 `search_papers`；OpenAlex 要有 `search_works` |
| 3 | `tools/call` 實際搜尋回傳結果 | 帶憑證發一次真實查詢（query = `machine learning`），確認線上可用 |

憑證處理：`.mcp.json` 裡的 `${VAR:-}` 佔位會從 `.claude/settings.local.json` 的 `env` 展開後傳入子行程環境（Semantic Scholar 用 `SEMANTIC_SCHOLAR_API_KEY`；OpenAlex 用 `OPENALEX_EMAIL`／`OPENALEX_API_KEY`）。**金鑰只進子行程、不會被印出**；輸出僅顯示「哪些憑證有設」的布林狀態。

此測試**直接啟動 server**驗證，與 Claude Code session 內 `/mcp` 是否已掛載無關——不必先重啟 session 也能測。

### 預期輸出（範例）

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

### 疑難排解

- **`[FAIL] … no initialize/serverInfo response`**：前置工具缺失。`semantic-scholar` 需 `uv`／`uvx` 與 `git`；`openalex` 需 Node.js（`npx`）。見 [`install.md`](install.md)。首次執行 `uvx`／`npx` 會下載套件，較慢屬正常，腳本已放寬逾時。
- **`tools/call` 失敗但前兩項通過**：多半是網路或速率限制。OpenAlex 建議填 `OPENALEX_EMAIL`（polite pool）；Semantic Scholar 填 `SEMANTIC_SCHOLAR_API_KEY` 可提速。
- **`not found in .mcp.json`**：對應 server 未設定；檢查專案根目錄 `.mcp.json` 的 `mcpServers`。

## 2. 擷取層自測（source-document-extraction）

`source-document-extraction` 是全 suite 唯一含確定性擷取邏輯的 skill（另一支有腳本的 `markdown-to-word` 只做格式轉換）。改過 `scripts/` 下任一腳本後跑這兩支：

```bash
conda run -n research python .claude/skills/source-document-extraction/tests/test_clean_docx_markdown.py
conda run -n research python .claude/skills/source-document-extraction/tests/test_extract_pdf.py
```

### 測試內容

| 腳本 | 涵蓋 | 需要外部檔案？ |
|---|---|---|
| `test_clean_docx_markdown.py` | Word 清理的三個步驟（base64 圖片換佔位標記、書籤錨點與目錄連結還原、安全標點反跳脫）、`--keep-images` 行為、CLI 進入點，以及**字元守恆斷言** | 否，以合成字串驗證 |
| `test_extract_pdf.py`（自足組） | `--figures` 出圖：exit 0、確實寫出 PNG、遵守 `--pages`、預設模式仍寫出 `.md` | 否，腳本自製臨時 PDF |
| `test_extract_pdf.py`（後端組） | 兩後端與各模式：標題／表格數、清理後無反引號／HTML／粗體且標題 ≤5、`--no-clean` 保留原始標記、`--legacy` 頁分隔、`--raw`／`--outline`／`--pages` | **是**，須以 `SDE_TEST_PDF` 指定 |

`test_clean_docx_markdown.py` 最關鍵的是**字元守恆斷言**，用來守住清理器的核心不變式「只動標記、不動文字」：`unescape_punct` 只拿掉反斜線，故中文與英數字元皆須完全守恆；錨點與圖片兩步各自會丟掉 markup 識別字與二進位 payload（兩者都不是文字），故只斷言中文守恆，其可見文字是否保留由 toc／heading／external-link 三項檢查涵蓋。**放寬 `_SAFE_ESCAPE` 的字元集前，務必先確認還原後不會產生 Markdown 語法，並讓這組斷言維持通過。**

### 後端組：自備 PDF

本技能**不隨附測試用 PDF**（第三方文件不進版控），故後端組預設略過。要跑就用 `SDE_TEST_PDF` 指向本機任一份含標題與表格的 PDF（學術論文或計畫書皆可）——斷言刻意寫成 fixture-agnostic，換任何一份結構正常的 PDF 都應通過：

```bash
SDE_TEST_PDF="path/to/paper.pdf" conda run -n research python .claude/skills/source-document-extraction/tests/test_extract_pdf.py
```

### 預期輸出（未設 `SDE_TEST_PDF`）

```text
NOTE: SDE_TEST_PDF not set. Backend tests skipped; only the self-contained --figures group ran. To run them, point it at any PDF with headings and tables, e.g.
      SDE_TEST_PDF="path/to/paper.pdf" conda run -n research python tests/test_extract_pdf.py
[PASS] --figures exit 0 (done -> C:\Users\...\Temp\...)
[PASS] --figures wrote sample-p1.png
[PASS] --figures respects --pages (no p2)
[PASS] default mode writes .md text
ALL PASS
```

`test_clean_docx_markdown.py` 則印 24 行 `[PASS]` 後 `ALL PASS`，無條件執行、無提示。

### 疑難排解

- **`ModuleNotFoundError: fitz` / `mammoth`**：環境未裝齊，見 [`install.md`](install.md) 第 3 節。
- **`UnicodeEncodeError` 或 `conda run` 自己崩潰**：`conda run` 以 cp950 轉印子行程輸出，測試印到 stdout 的字串一律限 ASCII。新增輸出時延續 `ascii_safe()` 慣例（見該腳本模組 docstring）。

## 3. Skill frontmatter 測試

```bash
conda run -n research python tests/test_skill_frontmatter.py
```

**改動任何 `SKILL.md` 的 frontmatter 後必跑。** 全形冒號 `：` 混進 frontmatter 的 key（如 `description：`）會讓 YAML 解析失敗、**整個 skill 靜默無法載入**——沒有錯誤訊息，只是不見了。此測試就是為了攔下這一類。全過印 `ALL PASS`。

必要鍵為 `name` 與 `description`。`version` 是本 suite 的慣例、不是 Agent Skills 規格要求，故視為選用——**外部匯入（vendored）的 skill 不帶 `version` 屬正常**，該行會標成 `[no version]` 而非失敗：

```text
[PASS] paper-search  (name, description, version)
[PASS] source-document-extraction  (name, description)  [no version]
------------------------------------------------------------
ALL PASS (13 SKILL.md)
```
