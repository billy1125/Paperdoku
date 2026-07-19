---
name: literature-review-organizer
description： 整理和分析多篇學術論文，支援上傳的PDF文件或論文連結，比較多篇論文、萃取核心論點、建立文獻比較表、整理理論脈絡、辨識研究缺口、提出未來研究方向，或生成可直接用於文獻回顧與研究提案的繁體中文輸出。本 skill 是「綜整型」多篇整理（焦點在綜整、缺口與寫作）。注意路由：若要逐一評估各篇的假設建構邏輯與支持狀態（評估型，非綜整），改用 paper-research-logic-review；若要抽取單篇的研究方法架構，改用 method-extraction-social-science；若只讀單篇深入理解，改用 paper-reading-zh。
version: 0.1.0
---

# 文獻整理與研究綜整

接收多篇文獻 PDF、DOI、出版社頁面或其他論文連結。先做開場詢問，再依流程執行。輸出以 Markdown 格式呈現，預設語言為繁體中文。

## 開場詢問

> 邊界自檢：本 skill 是**綜整型**——焦點在比較、研究缺口、未來方向與文獻回顧撰寫。若使用者其實要的是逐一評估各篇假設建構邏輯與支持狀態（評估型），改用 `paper-research-logic-review`；要抽單篇方法架構改用 `method-extraction-social-science`。不確定時先確認，不硬做。

收到文獻後，先問使用者：

> 請問你主要想達成什麼目的？
>
> 1. **研究缺口分析**：找出文獻還沒解決的問題，支持研究動機（適合已有方向）
> 2. **研究方向探索**：廣泛列出可發展的題目與假說（適合選題階段）
> 3. **文獻回顧撰寫**：整合成可直接貼入論文的段落初稿（適合論文寫作中）
> 4. **主題快速掌握**：只需整體輪廓與重點比較（適合初步了解）

根據選擇調整輸出重點：

| 選擇 | 輸出重點 |
|---|---|
| 1 研究缺口分析 | 深度缺口分析，明確區分作者明示 vs 綜合推論，說明每個缺口的重要性 |
| 2 研究方向探索 | 廣泛研究題目、假說方向、可能的 conceptual framework |
| 3 文獻回顧撰寫 | 整合段落初稿，著重脈絡敘述與引用整合 |
| 4 主題快速掌握 | quick scan 模式：比較表 + 每篇 3 點重點 + 初步共識 |

## 工作流程

確認目的後，依下列順序執行，不跳步：

1. 盤點來源並判斷可讀程度（規則見 `references/extraction-rules.md`）
2. 逐篇擷取核心資訊（欄位清單見 `references/extraction-rules.md`）
3. 建立統一欄位的比較表（格式見 `references/output-template.md`）
4. 撰寫逐篇文獻整理（格式見 `references/output-template.md`）
5. 進行跨文獻綜整（結構見 `references/output-template.md`）
6. 彙整研究缺口與未來研究方向（分類與判斷規則見 `references/analysis-framework.md`）
7. 視需要補充深度輸出（選項見 `references/output-template.md` 的「可選加值輸出」）

quick scan 模式只執行步驟 1–3 與步驟 6 的初步版本。

## 深度模式

預設為 **standard review**，使用者可指定。

| 模式 | 適合情境 | 包含內容 |
|---|---|---|
| quick scan | 快速主題掃描 | 比較表、每篇 3 點重點、初步缺口 |
| standard review | 一般文獻整理 | 比較表、逐篇整理、跨文獻綜整、缺口總整理、未來方向 |
| deep review | 論文/研究提案前期 | standard 全部 + 變數關係、文獻回顧草稿、研究問題假說、conceptual framework |
| systematic review | 要做可重現的系統性回顧 | PRISMA 流程（識別→篩選→符合資格→納入）＋ 明列納入/排除準則 ＋ 逐篇 RoB ＋ 綜整；詳見 `references/mode-systematic-review.md` |

> `systematic review` 模式不是把 standard 做多一點——它要求**可重現的篩選紀錄**（每篇為何納入/排除、各階段計數）與**風險偏誤評估**，適合真的要寫 SR/PRISMA 的使用者。流程與輸出見 `references/mode-systematic-review.md`。

## 核心限制

- 不捏造作者未寫出的結論、理論或研究缺口
- 摘要頁資訊不得誤寫成全文分析結果
- 資訊不足時降低語氣確定程度並明示限制
- 文獻高度異質時改寫成分群式結論，不硬湊單一結論

## 上下游交接

- **產物**：綜整／比較表／回顧成品寫成 markdown 存到 `reports/`（檔名依主題＋模式，見 `../_shared/paper_naming_convention.md`）。
- **上游**：PDF 先經 `source-document-extraction` 抽成 `extracted/*.md`；候選清單可承接 `paper-search`；逐篇方法可承接 `method-extraction-social-science`。
- **本 skill 常是綜整層終點**。`systematic review` 模式會呼叫 `citation-verification-zh`（查引用）與 `../_shared/risk_of_bias.md`（逐篇 RoB）。鏈見 `../_shared/handoff.md`。
