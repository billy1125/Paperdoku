# 安裝與前置需求

本檔集中列出 Paperdoku 的所有外部相依與安裝程序。外部相依集中在三個 skill（`paper-search`、`citation-verification-zh`、`source-document-extraction`，外加匯出用的 `markdown-to-word`）；其餘 5 個閱讀/分析 skill（`paper-reading-zh`、`academic-peer-review-zh`、`paper-research-logic-review`、`literature-review-organizer`、`method-extraction-social-science`）為 prompt 驅動，**不需任何外部安裝**。

## 總覽

| 需求 | 用途 | 誰需要 | 必要性 |
|---|---|---|---|
| Claude Code（最新版） | 執行整個 skill suite 的平台 | 全部 | 必要 |
| `uv`（提供 `uvx`） | 執行 Semantic Scholar MCP server | `paper-search`、`citation-verification-zh` | 必要（用 Semantic Scholar 時） |
| `git` | `.mcp.json` 以 `uvx --from git+https://…` 取件，需 git 才能 clone | `paper-search`、`citation-verification-zh` | 必要（用 Semantic Scholar 時） |
| Semantic Scholar API key | 提高查詢速率上限 | `paper-search`、`citation-verification-zh` | 選用（免費） |
| Node.js（含 `npx`） | 執行 OpenAlex MCP server | `paper-search`、`citation-verification-zh` | 必要（用 OpenAlex 時；裝 Claude Code 已含） |
| OpenAlex email／API key | polite pool 提速／premium 存取 | `paper-search`、`citation-verification-zh` | 選用（email 免費、建議填） |
| conda + Python 3.11 + 擷取套件 | PDF/Word → 結構化 Markdown | `source-document-extraction` | 必要 |
| `pypandoc` + conda-forge `pandoc` | Markdown 報告 → Word `.docx` | `markdown-to-word` | 選用（要匯出 Word 時） |

`paper-search` 與 `citation-verification-zh` 有**兩個可用資料源 MCP**（Semantic Scholar 與 OpenAlex），可擇一或併用；只想用其中一個時，另一個的前置可略過。

## 1. Claude Code

安裝最新版 Claude Code（需 Node.js 18 以上）：

```bash
npm install -g @anthropic-ai/claude-code
```

## 2. Semantic Scholar MCP（paper-search 與 citation-verification-zh）

兩個資料源 MCP 採**專案層級安裝**：設定寫在**專案根目錄的 `.mcp.json`**，從 repo 根目錄啟動 `claude` 時自動載入（首次會提示是否信任專案 MCP，選允許即可）。此檔以 `${VAR:-}` 引用金鑰、不含明文，隨整包專案一起版控／搬移。裝好後在 Claude Code 輸入 `/mcp` 應看到兩個 server connected。

其一 `semantic-scholar` MCP server 由 `uvx` 執行、套件來源為 `git+https://github.com/akapet00/semantic-scholar-mcp`。因此需先安裝 **`uv`（提供 `uvx`）** 與 **`git`**（clone 取件用）；**兩者缺一 MCP 無法啟動，這兩個 skill 就不能動作**。

### 2.1 安裝 uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2.2 安裝 git

依作業系統另行安裝（macOS 可用 Xcode Command Line Tools 或 Homebrew；Windows 見 <https://git-scm.com/download/win>；Linux 用套件管理器）。

### 2.3 驗證

```bash
uv --version && git --version
```

兩者均有輸出即可。

### 2.4 API key（選用，免費）

前往 <https://www.semanticscholar.org/product/api> 申請，將金鑰填入 **`.claude/settings.local.json`** 的 `env.SEMANTIC_SCHOLAR_API_KEY`（從 `.claude/settings.local.json.example` 複製後填入）。此檔已被 gitignore，`.mcp.json` 僅以 `${SEMANTIC_SCHOLAR_API_KEY:-}` 引用，金鑰不進版控。

- 填入或修改金鑰後需**重啟 Claude Code session** 才生效。
- 無金鑰仍可跑，但與匿名用戶共用速率限制、較容易被限速。
- 申請與設定細節另見 [`paper-search/README.md`](../.claude/skills/paper-search/README.md)。

### 2.5 確認連線

在 Claude Code 輸入 `/mcp`，看到 `semantic-scholar` 顯示 connected 即成功。MCP 未連線時，`citation-verification-zh` 會誠實告知無法查核、**不憑記憶判定**（呼應 anti-leakage）。

## 2b. OpenAlex MCP（同上兩個 skill 的第二資料源）

第二個資料源 `openalex`，由 `.mcp.json` 以 **`npx`** 執行 `openalex-research-mcp`（Node/TypeScript，MIT 授權）。涵蓋 2.4 億篇以上學術著作，另含引用網路、期刊分級、開放取用版本等 31 個工具。與 Semantic Scholar 可擇一或併用（引用查核時兩源互補、降低偽陰性）。

### 2b.1 前置：Node.js

`npx` 隨 Node.js 附帶；安裝 Claude Code 時已需 Node.js 18 以上，通常無須另裝。驗證：

```bash
node --version && npx --version
```

`npx -y openalex-research-mcp` 首次執行會自動下載套件，無須手動 `npm install`。

### 2b.2 email 與 API key（皆選用）

OpenAlex 基本查詢**免金鑰、完全開放**。兩個環境變數放進 **`.claude/settings.local.json`** 的 `env`（已 gitignore）：

- `OPENALEX_EMAIL`：填你的 email 即加入 polite pool，速率上限由 10 提到 100 req/s。**建議填**。
- `OPENALEX_API_KEY`：僅 OpenAlex Premium 用戶需要；沒有就留空字串。

`.mcp.json` 以 `${OPENALEX_EMAIL:-}`／`${OPENALEX_API_KEY:-}` 引用，金鑰不進版控。填入或修改後需**重啟 Claude Code session**。

### 2b.3 確認連線

在 Claude Code 輸入 `/mcp`，看到 `openalex` 顯示 connected 即成功。

## 3. source-document-extraction（PDF/Word 擷取）

需 conda 環境 `research`（Python 3.11，跨平台）與擷取套件：

```bash
conda create -n research python=3.11 -y
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
```

驗證環境：

```bash
conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"
```

以實際 PDF fixture 自測（不依賴 pytest；全過印 `ALL PASS`、以 0 退出；fixture 見該 skill）：

```bash
conda run -n research python .claude/skills/source-document-extraction/tests/test_extract_pdf.py
```

裸 `python`/`pip` 已於 `.claude/settings.json` 封鎖；一律走 `conda run -n research`。詳細選項見該 skill 的 [`SKILL.md`](../.claude/skills/source-document-extraction/SKILL.md) 與 [`CLAUDE.md`](../.claude/skills/source-document-extraction/CLAUDE.md)。

## 4. 驗證兩個資料源 MCP

裝好後可跑連線測試確認 `semantic-scholar` 與 `openalex` 皆可實際查詢——**自己在終端機執行**，或直接**請 Claude 代為執行**：

```bash
conda run -n research python tests/test_mcp_servers.py
```

全部通過會印 `ALL PASS`。測試的細節與疑難排解見 [`test.md`](test.md)。

## 5. markdown-to-word（Markdown 報告 → Word .docx）

把 `reports/` 內的 markdown 報告（精讀摘要、審查意見書、綜整回顧等）轉成 Word `.docx`，供交稿或套期刊樣式範本。以 **Pandoc（透過 `pypandoc`）** 轉換：GFM pipe table 會變成 Word 原生表格。與 `source-document-extraction` 共用同一個 conda 環境 `research`（Python 3.11，跨平台）。

```bash
conda create -n research python=3.11 -y                 # 若尚未建立
conda run -n research pip install pypandoc              # Python 封裝
conda install -n research -c conda-forge pandoc -y      # 原生 pandoc 二進位，全平台通用
```

驗證 pandoc 可用：

```bash
conda run -n research python -c "import pypandoc; print(pypandoc.get_pandoc_path())"
```

有印出 pandoc 路徑即可。實際轉檔範例（沿用來源報告主幹、副檔名改 `.docx`）：

```bash
conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py reports/報告.md -o reports/報告.docx
```

> **勿用 `pypandoc_binary`**：其內含的 pandoc 為 x86_64，macOS Apple Silicon 無 Rosetta 時會報 `bad CPU type in executable`；請改用 conda-forge 的原生 `pandoc`（各平台皆有對應 build）。選項與已知限制見該 skill 的 [`SKILL.md`](../.claude/skills/markdown-to-word/SKILL.md)。
