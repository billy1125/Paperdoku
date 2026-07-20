---
name: paper-reading-zh
description: 對「單篇」學術論文的多模式閱讀助手，四種模式：quick-scan（WHY／HOW／WHAT 快掃，判斷是否值得細讀）、full（逐章精讀＋整體分析＋初步評論，預設）、socratic（引導式提問幫你自己讀懂）、claim-audit（針對某個宣稱回原文查證據是否支持）。當使用者上傳或貼上一篇論文（PDF、文字、或網頁連結）：要求「精讀／逐章摘要／這篇在講什麼／目的／研究缺口／結論／節錄原文」用 full；「快速掃一下／值不值得讀／三分鐘看懂」用 quick-scan；「帶我讀／我想自己讀懂／用問題引導我」用 socratic；「這個宣稱有沒有根據／查一下這句／證據夠不夠」用 claim-audit。即使只說「幫我看一下這篇」，只要對象是單篇論文且偏深入理解全文，也用此 skill。注意路由：一次比較多篇改用 paper-research-logic-review（假設邏輯）或 literature-review-organizer（綜整）；只抽研究方法改用 method-extraction-social-science；完整同儕審查（逐條 Major／Minor＋Accept／Reject 審查意見書）改用 academic-peer-review-zh。
version: 0.1.0
---

# 單篇論文閱讀（繁體中文）

幫助使用者讀懂「一篇」論文，依需求切換四種模式。全程使用繁體中文，但保留必要的英文專有名詞與方法術語（例如 collaborative filtering、XAI、p-value），不要硬翻成生硬中文（見 `../_shared/output_language.md`）。

> **最高原則（Anti-leakage）**：一律以眼前這篇論文的原文為準，禁止用模型記憶補完論文內容；不在原文的標記為未提及，不捏造。完整鐵律見 `../_shared/anti_leakage.md`。讀不到全文（只有摘要／擷取不完整）時，依 `../_shared/confidence_language.md` 收語氣、明示範圍。

## 模式選擇

先判斷（或詢問）使用者要哪一種，**預設 `full`**：

| 模式 | 何時用 | 產出 | 規格 |
|---|---|---|---|
| `quick-scan` | 快速判斷一篇值不值得細讀 | WHY／HOW／WHAT 三段快掃 | `references/mode-quick-scan.md` |
| `full`（預設） | 深入精讀單篇 | 逐章摘要 → 整體分析 → 初步評論 | 下方各節 ＋ `references/output-template.md` |
| `socratic` | 想自己讀懂、要引導思考 | 一系列引導提問，不直接給結論 | `references/mode-socratic.md` |
| `claim-audit` | 查某個宣稱是否有原文證據支持 | 宣稱 → 原文證據 → 相稱判定 | `references/mode-claim-audit.md` |

模式不明時，用一句話問使用者要「快掃 / 精讀 / 引導我讀 / 查某個宣稱」，再進行。以下為 `full` 模式的完整規格。

---

## full 模式（預設）：逐章精讀

輸出由三大區塊組成：**逐章節摘要 → 整體分析 → 初步評論**。

### 開始之前：先判斷論文類型

精讀的重點會隨論文類型不同。讀完全文後，先在心裡判斷它屬於哪一類，再決定整體分析要強調什麼：

- **實證研究（empirical）**：有資料、假設、分析與結果。整體分析要能講清楚研究假設、如何驗證、結果是否支持假設。
- **綜述／立場論文（survey / review / position）**：整理與分類既有研究，通常沒有假設與統計結果。此時不要硬找「假設」或「實驗結果」——明說它沒有實證資料，價值在於整理與分類。
- **方法／系統論文（method / system）**：提出新方法或系統。整體分析要講清楚它解決了什麼、與既有方法相比的差異與貢獻。

判斷錯類型是最常見的失誤。例如把綜述論文當成實證論文，硬去找不存在的假設，會誤導使用者。寧可在輸出末尾誠實點出「這是綜述論文，沒有可供檢驗的假設或統計結果」。

### 輸出結構

固定依序輸出三部分，完整的模板、逐項規則與拿捏原則見 `references/output-template.md`：

1. **各章節摘要**：沿用論文原本的章節順序與編號，逐章（必要時逐小節）抓骨架。
2. **整體分析**：研究目的、要解決的問題、研究缺口、整體結論；實證論文再補假設與驗證結果。
3. **初步的論文評論**：讀懂全文後的輕量評論（主要貢獻、證據與宣稱是否相稱、明顯疑點、限制）。這是精讀的自然延伸，不是完整同儕審查；要針對某宣稱回原文查證改用本 skill 的 `claim-audit` 模式，要完整批判性審查（逐條 Major／Minor＋判決）改用 `academic-peer-review-zh`。

三部分都要完成，且每一部分都在**真正關鍵之處**嵌入一句原文節錄。這麼做是為了讓使用者能回到原文查證與定位，不是為了逐句照抄——節錄的判準（哪些該引、如何標示、不翻譯不重製）同樣見 `references/output-template.md` 的「原文節錄原則」。

### 風格

- 語氣像一位讀過全文、願意把骨架講清楚的同學或助教，不要像論文摘要那樣乾。
- 善用「定義 → 分類 → 差異 → 為何重要」的鋪陳，幫助使用者建立心智模型。
- 結尾可主動提一句後續選項（例如：可以改做成 Markdown／Word 檔，或轉成表格格式），但不要長篇大論。

完整的示範輸出（可解釋推薦系統綜述論文，含三部分與結尾提醒）見 `references/example-output.md`。

## 上下游交接

- **產物**：full 模式的精讀報告寫成 markdown 存到 `reports/`（檔名沿用來源主幹＋`reading`，見 `../_shared/paper_naming_convention.md`）；quick-scan／claim-audit 若需留存亦同，socratic 為互動引導通常不留檔。
- **上游**：PDF 先經 `source-document-extraction` 抽成 `extracted/*.md` 再讀，不對 PDF 直接動手。
- **下游**：精讀後要**完整同儕審查**用 `academic-peer-review-zh`；要查**參考文獻真偽**用 `citation-verification-zh`。收尾可主動提示。鏈見 `../_shared/handoff.md`。
