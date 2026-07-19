# paper-search — Semantic Scholar 論文搜尋技能：安裝與使用說明

## 這是什麼
一個跑在 Claude Code 裡的論文搜尋技能，透過 Semantic Scholar MCP
搜尋 2 億篇以上學術論文，自動整理成表格 + 摘要，可匯出 APA / BibTeX。

技能的行為規則（工作流程、輸出格式、注意事項）定義在 `SKILL.md`；
本檔僅說明安裝與啟動方式。

## 檔案結構
```
paper-search/
├── SKILL.md      # 論文搜尋技能定義（agent 自動讀取）
├── .mcp.json     # MCP 設定（需填入 API key）
├── README.md     # 本檔：安裝與使用說明
└── output/       # 搜尋結果輸出資料夾（執行時自動建立）
```

## 安裝步驟

### 1. 安裝 Node.js（18 以上）與 Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. 安裝 uv（執行 MCP server 用）
macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 申請 Semantic Scholar API Key（建議，免費）
前往 https://www.semanticscholar.org/product/api 申請，
然後打開 `.mcp.json`，把 `YOUR_KEY` 換成你的 key。
（沒 key 也能跑，但流量與其他匿名用戶共享，較容易被限速）

### 4. 啟動
```bash
cd paper-search
claude
```

### 5. 確認 MCP 連線
在 Claude Code 裡輸入：
```
/mcp
```
看到 semantic-scholar 顯示 connected 就成功了。

## 使用範例
```
> 幫我找近五年關於遊戲化學習對大學生學習動機影響的高引用論文，要10篇

> 第 3 篇和第 7 篇幫我看詳細摘要，它們用什麼研究方法

> 把這10篇匯出成 BibTeX
```

## 疑難排解
- MCP 連不上 → 確認 uv 已安裝（終端機輸入 `uv --version` 測試）
- 搜尋很慢或被限速 → 確認已填入 API key
- 找不到論文 → 試試換英文關鍵字，或請 agent 調整搜尋詞
