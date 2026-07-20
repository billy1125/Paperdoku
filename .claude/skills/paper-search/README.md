# paper-search — 論文搜尋技能：安裝與使用說明

## 這是什麼
一個跑在 Claude Code 裡的**論文搜尋技能**：依關鍵字搜尋學術論文、追蹤引用關係，
自動整理成表格 + 摘要，可匯出 APA / BibTeX。

論文資料透過 MCP 取得。**目前有兩條可用管道，可擇一或併用**：

- **Semantic Scholar**——2 億篇以上論文。
- **OpenAlex**——2.4 億篇以上，另含引用網路、期刊分級、開放取用版本等分析工具。

技能的行為規則（工作流程、輸出格式、注意事項）定義在 `SKILL.md`；
本檔僅說明安裝與啟動方式，完整前置需求另見專案 `docs/install.md`。

> MCP 採**專案層級安裝**：設定放在**專案根目錄的 `.mcp.json`**（不在本資料夾），
> 內含 `semantic-scholar` 與 `openalex` 兩個資料源；金鑰／email 放在
> `.claude/settings.local.json`。從專案根目錄啟動 `claude` 即自動載入。

## 檔案結構
```
Paperdoku/
├── .mcp.json                       # MCP 設定（專案層級，${VAR:-} 引用金鑰）
├── .claude/settings.local.json     # 金鑰／email（gitignore，不進版控）
└── .claude/skills/paper-search/
    ├── SKILL.md                    # 論文搜尋技能定義（agent 自動讀取）
    ├── README.md                   # 本檔：安裝與使用說明
    └── output/                     # 搜尋結果輸出資料夾（執行時自動建立）
```

## 安裝步驟

### 1. 安裝 Node.js（18 以上）與 Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 安裝兩條管道的執行環境（可擇一或併用）

- **Semantic Scholar**：需 `uv`（提供 `uvx`）與 `git`（`git` 請依作業系統另裝）。安裝 uv：
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows (PowerShell)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **OpenAlex**：需 Node.js（步驟 1 已裝，`npx` 隨附），無須另裝。

### 3. 設定金鑰／email（皆選用、免費）
都填在 `.claude/settings.local.json`（從 `.claude/settings.local.json.example` 複製改名；已 gitignore）。
根目錄 `.mcp.json` 以 `${VAR:-}` 引用，皆不進版控。兩者都沒填也能跑，只是與匿名用戶共用速率、較易被限速。

- **Semantic Scholar**：`SEMANTIC_SCHOLAR_API_KEY`，申請 https://www.semanticscholar.org/product/api
- **OpenAlex**：`OPENALEX_EMAIL`（建議，polite pool 把速率上限由 10 提到 100 req/s）與選用的 `OPENALEX_API_KEY`（premium）

### 4. 啟動
從**專案根目錄**啟動（專案層級 `.mcp.json` 才會被載入）：
```bash
cd Paperdoku
claude
```
首次啟動會提示是否信任專案 MCP，選允許。填改金鑰後需重啟 session 生效。

### 5. 確認 MCP 連線
在 Claude Code 裡輸入：
```
/mcp
```
看到 `semantic-scholar`（及 `openalex`，若已設定）顯示 connected 就成功了。

## 使用範例
```
> 幫我找近五年關於遊戲化學習對大學生學習動機影響的高引用論文，要10篇

> 第 3 篇和第 7 篇幫我看詳細摘要，它們用什麼研究方法

> 把這10篇匯出成 BibTeX
```

## 疑難排解
- MCP 連不上 → 確認該管道前置已裝（Semantic Scholar 需 `uv`／`git`；OpenAlex 需 Node.js），已從專案根目錄啟動並重啟過 session
- 搜尋很慢或被限速 → 確認已填 API key／email
- 找不到論文 → 換英文關鍵字，或改用另一個資料源再查一次
