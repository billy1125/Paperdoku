---
name: paper-search
description: 當使用者要搜尋學術論文、做文獻探索、查找特定主題的研究、追蹤論文引用關係，或要求整理某主題的文獻清單時使用。透過 Semantic Scholar MCP 取得論文資料。注意路由：本 skill 只負責搜尋與列清單；要對找到的多篇做深度比較，改用 paper-research-logic-review 或 literature-review-organizer；要精讀單篇改用 paper-reading-zh。
version: 0.1.0
---

# 論文搜尋技能

## 前置需求與環境檢查
本技能有**兩個可用的資料源 MCP server**（專案層級安裝，設定於專案根目錄 `.mcp.json`），可擇一或併用：

- `semantic-scholar`（以 `uvx` 執行 semantic-scholar-mcp）——涵蓋 2 億篇以上論文。
- `openalex`（以 `npx` 執行 openalex-research-mcp）——涵蓋 2.4 億篇以上論文，另含引用網路、期刊分級、開放取用版本等分析工具。

執行搜尋前若發現 MCP 工具不可用，**不要憑記憶回答論文資訊**，改為引導使用者依序排查：

1. 在 Claude Code 輸入 `/mcp`，確認要用的 server（`semantic-scholar` 或 `openalex`）顯示 connected
2. 確認前置工具已安裝：`semantic-scholar` 需 `uv`（`uv --version`）與 `git`；`openalex` 需 Node.js（`node --version`，`npx` 隨附）
3. 確認 `.claude/settings.local.json` 的金鑰／email 已填妥（可從 `.claude/settings.local.json.example` 複製；此檔已被 gitignore，不進版控）：Semantic Scholar 用 `SEMANTIC_SCHOLAR_API_KEY`；OpenAlex 用 `OPENALEX_EMAIL`（polite pool，把速率上限由 10 提到 100 req/s）與選用的 `OPENALEX_API_KEY`（premium）。填入或修改後需重啟 Claude Code session 才會生效。

兩者皆無金鑰亦可執行（共用匿名速率、較易被限速）。安裝細節見專案 `docs/install.md`。

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
依現有連線的 server 選工具（一組關鍵字結果不理想時，換同義詞或更精確的詞組再搜，例如把 "AI writing" 換成 "generative AI academic writing"）：

**Semantic Scholar MCP：**
- `search_papers` 或 `paper_relevance_search`：關鍵字搜尋，帶入 year、fields_of_study、min_citation_count 等 filter
- `get_paper`：取得單篇完整資訊（abstract、DOI、引用數）
- `get_citations`：追蹤引用（誰引用此文 / 此文引用誰）

**OpenAlex MCP（工具名以實測 `tools/list` 為準）：**
- `search_works`：關鍵字搜尋；`search_by_topic` 依主題探索；`autocomplete_search` 補全查詢詞
- `get_work`：取單篇 metadata；`get_related_works` 取相關文獻；`find_open_access_version` 找開放取用版本
- `get_work_citations` / `get_work_references` / `get_citation_network`：正向被引、反向引用、引用網路；`get_top_cited_works` 取高被引
- `find_review_articles` 找回顧文章、`find_seminal_papers` 找奠基之作；`check_venue_quality` / `list_journal_presets`（UTD24、FT50、AJG 等分級）做期刊品質篩選

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
