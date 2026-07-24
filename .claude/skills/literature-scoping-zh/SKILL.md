---
name: literature-scoping-zh
description: 研究設計 pipeline（前段）的文獻盤點步——在「發現期」把某主題的搜尋結果系統性盤點成文獻地圖：規劃搜尋策略、透過論文資料庫 MCP（Semantic Scholar／OpenAlex）掌握文獻版圖、辨識主題群集、標定研究缺口，供決定研究定位。當使用者要「盤點某主題的文獻版圖」「這個領域目前做到哪、還缺什麼」「幫我把這批搜尋結果整理成文獻地圖並找缺口」「我要定位我的研究在文獻中的位置」時使用。輸出繁體中文，產物寫到 research-design/<主題>-scoping.md。注意路由與界線：本 skill 在「發現期」運作、吃 paper-search 的候選清單或 MCP metadata（未必有全文），輸出「盤點＋缺口地圖」以定研究方向，屬前段 pipeline；若要對「手上已有全文（extracted/*.md）的多篇論文」做綜整寫作、寫正式文獻回顧、跑完整 PRISMA systematic review 與逐篇 RoB，改用後段 pipeline 的 literature-review-organizer。只搜尋列清單改用 paper-search；查引用是否真實存在改用 citation-verification-zh。兩條 pipeline 不混用。
version: 0.1.0
---

# 文獻系統性盤點技能（Literature Scoping）

研究設計 pipeline（前段）的第二/三步。用途是**在動筆細讀之前，把某主題的文獻版圖盤點清楚、標出研究缺口**，讓使用者決定研究定位與下一步該深讀哪些。產物是「盤點＋缺口地圖」提案，不是正式的文獻回顧稿。遵守 `../_shared/research_design_discipline.md`（尤其**反缺口膨脹**）、`../_shared/anti_leakage.md`、`../_shared/output_language.md`、`../_shared/confidence_language.md`、`../_shared/evidence_hierarchy.md`。

## 與後段 literature-review-organizer 的界線（重要）

| | `literature-scoping-zh`（前段、本 skill） | `literature-review-organizer`（後段） |
|---|---|---|
| 階段 | 發現期，動筆讀之前 | 拿到論文之後 |
| 吃什麼 | `paper-search` 候選清單／MCP metadata（可能只有題名/摘要/引用數） | `extracted/*.md` 全文 |
| 做什麼 | 盤點版圖、群集、標缺口、定研究定位 | 綜整寫作、比較表、完整 PRISMA systematic review、逐篇 RoB |
| 產物 | `research-design/<主題>-scoping.md` | `reports/*.md` |

要寫正式回顧、逐篇讀全文做 RoB → 導去後段。本 skill 只到「該深讀哪些、缺口在哪」為止。

## 適用情境

- 「幫我盤點『X 主題』的文獻版圖，這領域做到哪、還缺什麼」
- 「把這批 paper-search 結果整理成文獻地圖並標研究缺口」
- 「我要定位我的研究在既有文獻中的位置」

## 工作流程

### 步驟 1：界定盤點問題與範圍

用 PICO／PECO 或「主題＋方法＋對象」框定核心問題（例：generative AI（I）對本科生學術寫作（P）的影響（O））。定清楚：2–4 個核心概念、時間範圍、領域 fields_of_study、納入/排除傾向（peer-reviewed／preprint、研究設計）。資訊不足時一次問齊，不逐題問。

### 步驟 2：規劃搜尋策略並執行（接 paper-search／MCP）

每個核心概念列同義詞、縮寫、相關詞，規劃布林組合。透過 `paper-search` 走 MCP 搜尋（`semantic-scholar` 的 `search_papers`；`openalex` 的 `search_works`／`search_by_topic`／`find_review_articles`／`find_seminal_papers`／`get_top_cited_works`／`check_venue_quality`）。**記錄搜尋策略**：資料源、查詢字串、年份、篩選、日期、命中數——缺口宣稱的可信度取決於此。搜尋策略與 MCP 取向的涵蓋盤點細節見 `references/scoping-strategy.md`。

MCP 不可用時，**不憑記憶捏造文獻**，誠實回報無法盤點並引導排查（見 `paper-search` 前置需求）。

### 步驟 3：篩選與去重（PRISMA-lite）

以核心問題篩題名與摘要，去重（優先 DOI，其次題名），記錄各階段計數：初始命中 → 去重後 → 題名/摘要篩選後 → 納入盤點。此為輕量計數流程，非後段的完整 PRISMA（完整 PRISMA + 全文逐篇 RoB 屬 `literature-review-organizer`）。

### 步驟 4：建立文獻地圖

把納入的文獻依**明確關係**分主題群集（研究問題／機制／對象／方法／理論框架／結果方向）。用 MCP metadata 標註每篇的年份、引用數、期刊分級（openalex `check_venue_quality`／`list_journal_presets`：UTD24、FT50、AJG 等）、是否為 seminal／review。可用 `get_citation_network`／`get_related_works` 補足版圖與引用脈絡。

### 步驟 5：標定研究缺口

依 `references/gap-taxonomy.md` 的缺口分類辨識：evidence gap（證據衝突/不足）、knowledge gap（未被探討的關係）、methodological gap（方法侷限）、population/context gap（對象或情境未涵蓋）、theoretical gap（理論整合不足）。**每個缺口都用「在本次搜尋範圍內尚未定位到直接證據」而非「從未有人研究」**，並附搜尋邊界，避免假缺口（反缺口膨脹，見共用紀律）。

### 步驟 6：定位與建議下一步

指出使用者的研究可切入哪個缺口、哪幾篇是**必讀關鍵文獻**（值得下載全文細讀），並建議下游動作。

## 輸出格式（產物）

寫成 markdown 存到 `research-design/<主題>-scoping.md`：

1. **盤點問題與範圍**（PICO／概念、納入排除）
2. **搜尋策略與涵蓋盤點**：資料源、查詢、年份、篩選、日期、PRISMA-lite 計數
3. **主題群集**（每群集一段綜述＋代表文獻）
4. **文獻地圖表**：| # | 題名 | 第一作者 et al. | 年 | 引用數 | 期刊/分級 | 群集 | 類型（seminal/review/primary） | 信心 |
5. **研究缺口清單**（分類＋搜尋邊界，避免膨脹）
6. **研究定位與必讀關鍵文獻**
7. **建議下一步**

引用數與期刊資訊一律來自 MCP 實際回傳，註明為查詢當下數字；摘要須改寫，禁止直接複製原文 abstract。

## 上下游交接

- **上游**：`research-brainstorming-zh`（發散出的方向）、`paper-search`（候選清單／BibTeX 於 `output/`）。
- **下游（橋接到後段）**：挑出的必讀關鍵文獻 → 使用者把 PDF 放進 `papers/` → `source-document-extraction` 抽成 `extracted/*.md` → 後段閱讀/審查/綜整層（`paper-reading-zh`、`literature-review-organizer` 等）。
- **下游（前段內）**：盤點結果與缺口 → `scholar-evaluation-zh`（篩查關鍵文獻可信度）→ `hypothesis-generation-zh`（收斂研究問題）。
- 收尾建議下一步、點出可傳產物，但不自動執行。完整鏈見 `../_shared/handoff.md`。

## 參考檔

- `references/scoping-strategy.md` — 搜尋策略規劃、MCP 取向的涵蓋盤點、PRISMA-lite 計數、引用鏈追蹤、盤點常見陷阱。
- `references/gap-taxonomy.md` — 研究缺口分類與辨識準則，以及反缺口膨脹的判斷。
