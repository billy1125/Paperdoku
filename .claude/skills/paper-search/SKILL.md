---
name: paper-search
description： 當使用者要搜尋學術論文、做文獻探索、查找特定主題的研究、追蹤論文引用關係，或要求整理某主題的文獻清單時使用。透過 Semantic Scholar MCP 取得論文資料。注意路由：本 skill 只負責搜尋與列清單；要對找到的多篇做深度比較，改用 paper-research-logic-review 或 literature-review-organizer；要精讀單篇改用 paper-reading-zh。
version: 0.1.0
---

# 論文搜尋技能

## 前置需求與環境檢查
本技能依賴 `semantic-scholar` MCP server（設定於本資料夾 `.mcp.json`，以 `uvx` 執行 semantic-scholar-mcp）。執行搜尋前若發現 MCP 工具不可用，**不要憑記憶回答論文資訊**，改為引導使用者依序排查：

1. 在 Claude Code 輸入 `/mcp`，確認 `semantic-scholar` 顯示 connected
2. 確認已安裝 uv（終端機輸入 `uv --version` 測試）
3. 確認 `.claude/settings.local.json` 的 `env.SEMANTIC_SCHOLAR_API_KEY` 已填入有效的 key（可從 `.claude/settings.local.json.example` 複製一份，改名為 `settings.local.json` 後填入；此檔已被 gitignore，不會進版控）。填入或修改後需重啟 Claude Code session 才會生效。

若搜尋很慢或被限速：提醒使用者前往 https://www.semanticscholar.org/product/api 申請免費 API Key 並填入 `.claude/settings.local.json`（沒有 key 也能執行，但流量與其他匿名用戶共享，容易被限速）。

## 適用情境
- 「幫我找關於 X 的論文」
- 「近五年 Y 主題有哪些高引用研究」
- 「這篇論文引用了哪些理論 / 被誰引用」
- 「整理一份 Z 領域的文獻清單」

## 標準工作流程

### 步驟 1：解析需求
從使用者敘述中抓出：
- 核心主題（轉成 2-3 組英文關鍵字）
- 領域 fields_of_study（如 Education, Business, Computer Science, Psychology, Medicine）
- 年份範圍
- 數量與排序偏好

資訊不足時一次性詢問，不要逐題問。

### 步驟 2：執行搜尋
使用 Semantic Scholar MCP 工具：
- `search_papers` 或 `paper_relevance_search`：關鍵字搜尋，帶入 year、fields_of_study、min_citation_count 等 filter
- 一組關鍵字結果不理想時，換同義詞或更精確的詞組再搜（例如把 "AI writing" 換成 "generative AI academic writing"）
- 需要時用 `get_paper` 取得單篇完整資訊（abstract、DOI、引用數）
- 需要追蹤引用時用 `get_citations`（誰引用此文 / 此文引用誰）

### 步驟 3：篩選
從原始結果中挑出真正相關的，過濾掉：
- 主題明顯偏離的
- 純會議摘要、預印本品質存疑的（除非使用者要最新研究）
- 重複項

### 步驟 4：呈現（預設格式）

**總覽表格：**
| # | 標題 | 第一作者 et al. | 年份 | 引用數 | 來源 |
|---|------|----------------|------|--------|------|

**逐篇摘要：** 每篇 2-4 句中文，涵蓋研究問題、方法、主要發現。摘要必須改寫，禁止直接複製原文 abstract。

### 步驟 5：提供下一步
搜尋後主動給選項：深入特定論文 / 追蹤引用網絡 / 匯出 BibTeX / 縮小或擴大搜尋範圍。

## 關鍵字技巧
- 學術搜尋用英文關鍵字命中率最高
- 用名詞片語而非完整句子：「transformer attention mechanism」優於「how does attention work in transformers」
- 主題 + 方法 + 對象的組合常更精準：例如 "gamification" + "motivation" + "undergraduate"

## BibTeX 匯出
若使用者要參考文獻：
- 用 MCP 工具取得各篇 metadata（含 DOI）
- 產生標準 BibTeX entry，存到 `output/references-[主題]-[日期].bib`（`output/` 資料夾不存在時先建立）
- 同時可提供 APA 第七版文字版清單

## 找不到論文時
- 換英文同義詞或更精確的詞組重搜，並向使用者說明調整了哪些搜尋詞
- Semantic Scholar 資料有覆蓋限制，仍找不到時誠實告知，可建議補用一般 web search 查實務資料

## 注意事項
- 所有論文資訊一律來自 MCP 實際回傳，絕不憑記憶捏造標題、作者或引用數
- 引用數會隨時間變動，呈現時可註明為查詢當下數字

## 上下游交接

- **本 skill 是發現層入口**（上游：無）。
- **下游**：找到候選後，若要細讀/分析，PDF 先經 `source-document-extraction` 抽成 `extracted/*.md`;metadata 與 BibTeX(`output/`)可直接餵 `literature-review-organizer` 或 `paper-research-logic-review`。
- 收尾時建議下一步（如「要細讀第 3 篇，先抽全文再用 paper-reading-zh」）。完整鏈見 `../_shared/handoff.md`。
