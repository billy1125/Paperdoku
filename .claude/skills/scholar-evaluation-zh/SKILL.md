---
name: scholar-evaluation-zh
description: 研究設計 pipeline（前段）的可信度檢驗步——以 ScholarEval 框架，對「別人已發表的關鍵文獻」做結構化可信度／品質評估與 5 分制評分（problem formulation、literature review、methodology、data、analysis、results、writing、citations 等維度），用來對前段挑出的重點文獻加權、判斷可不可信、值不值得倚重。當使用者要「評估這幾篇關鍵文獻可不可信」「這篇的方法/證據夠不夠扎實」「幫我判斷哪幾篇比較可靠、該倚重哪些」「給這些文獻的品質打個分數並排序」時使用。輸出繁體中文，產物寫到 research-design/<主題>-credibility.md。注意路由與界線：本 skill 是「發現期對已發表關鍵文獻做可信度篩查與加權」，**不下 Accept/Reject 判決、不是投稿審查**；要對「一篇投稿」產出完整同儕審查意見書並下 Accept/Minor/Major/Reject 判決，改用後段 pipeline 的 academic-peer-review-zh；要查參考文獻是否真實存在（揪幻覺引用）改用 citation-verification-zh；要查某宣稱在原文是否有證據改用 paper-reading-zh 的 claim-audit。兩條 pipeline 不混用。
version: 0.1.0
---

# 關鍵文獻可信度評估技能（Scholar Evaluation）

研究設計 pipeline（前段）的第四步。用途是**在決定研究定位時，篩查關鍵文獻的可信度與品質**，給結構化評估與 5 分制評分，讓使用者判斷「這幾篇文獻可不可信、該倚重哪些、哪些結論要打折」。這是**加權/篩查**，不是投稿審查，也不下判決。遵守 `../_shared/research_design_discipline.md`、`../_shared/anti_leakage.md`、`../_shared/output_language.md`、`../_shared/confidence_language.md`、`../_shared/evidence_hierarchy.md`；實證研究可套 `../_shared/risk_of_bias.md`。

本框架基於 ScholarEval（Moussa et al., 2025, arXiv:2510.16234），一個以文獻為據評估研究「soundness（方法的實證效度）與 contribution（相對既有研究的推進程度）」的檢索增強評估框架。

## 與後段 academic-peer-review-zh 的界線（重要）

| | `scholar-evaluation-zh`（前段、本 skill） | `academic-peer-review-zh`（後段） |
|---|---|---|
| 對象 | 別人**已發表**的關鍵文獻（可能多篇） | 一篇**投稿/待審**論文 |
| 目的 | 可信度篩查、加權、決定倚重哪些 | 完整審查意見書、給修改指引 |
| 產物 | 維度評分＋可信度排序＋加權建議 | 逐條 Major/Minor＋總體建議 |
| 判決 | **不下** Accept/Reject | **下** Accept／Minor／Major／Reject |

要對投稿下判決 → 後段。查引用真偽 → `citation-verification-zh`。查某宣稱有無原文證據 → `paper-reading-zh` 的 `claim-audit`。

## 適用情境

- 「評估這幾篇關鍵文獻可不可信、方法扎不扎實」
- 「幫我判斷這批文獻哪幾篇比較可靠、我該倚重哪些」
- 「給這些文獻的品質打分並排序，作為引用取捨依據」

## 可讀程度先決（anti-leakage）

評估**只能根據實際讀到的內容**。依 `../_shared/confidence_language.md` 先判斷每篇的可讀層次（全文/部分/僅摘要/幾乎不可讀），並讓評分的信心隨之收斂：只有摘要時，methodology／analysis／data 等維度多半只能標「資訊不足、待全文確認」，不可憑記憶或期刊名腦補。要細評方法品質，關鍵文獻應先經 `source-document-extraction` 抽成 `extracted/*.md`。

## 工作流程

### 步驟 1：界定評估對象與範圍

辨識文獻類型（實證/理論/回顧）與評估範圍：comprehensive（全維度）／targeted（只評特定面向，如 methodology）／comparative（多篇對比排序）。範圍模糊時先問。

### 步驟 2：逐維度評估

依 `references/evaluation-framework.md` 的準則與 rubric，對各適用維度給質性評估（2–3 個強項、2–3 個待改進、關鍵問題）與 5 分制評分：

1. Problem Formulation & Research Questions
2. Literature Review
3. Methodology & Research Design
4. Data Collection & Sources
5. Analysis & Interpretation
6. Results & Findings
7. Scholarly Writing & Presentation
8. Citations & References

純理論文章等不適用的維度（如 data collection）明確標為 not-applicable，不硬給分。

### 步驟 3：評分與整體判斷

5 分制：5 卓越／4 良好／3 尚可／2 待改進／1 不足。評分**透明列出**每維度得分與理由（Paperdoku 前段以 prompt 直接算加權平均並列出，不呼叫外部腳本）。維度權重可依情境調整（建議值見 references）。實證研究可另套 `../_shared/risk_of_bias.md` 六面向，結論強度對照 `../_shared/evidence_hierarchy.md`。

### 步驟 4：綜整整體評估

給每篇：整體品質判斷、3–5 個主要強項、3–5 個關鍵弱點、依影響力排序的優先改進點、（適用時）對目標的可信度定位。

### 步驟 5：可信度排序與加權建議

跨多篇時，輸出**可信度排序**與「該倚重哪些、哪些結論要打折、哪些需全文確認」的加權建議，供前段研究定位使用。

## 輸出格式（產物）

寫成 markdown 存到 `research-design/<主題>-credibility.md`：

1. **評估對象與範圍**（文獻清單、可讀層次、評估範圍）
2. **逐篇維度評估表**：| 維度 | 評分(1–5) | 強項 | 待改進 | 信心 |
3. **整體評估**（每篇：品質判斷＋強弱點）
4. **可信度排序與加權建議**
5. **（實證時）RoB 六面向摘要**
6. **建議下一步**

## 上下游交接

- **上游**：`literature-scoping-zh`／`paper-search` 挑出的關鍵文獻；細評方法需先 `source-document-extraction` 抽全文。
- **下游**：可信度加權後 → `hypothesis-generation-zh`（用較可信的證據收斂假設）；關鍵文獻要細讀/正式審查/綜整 → 後段 pipeline（`paper-reading-zh`、`academic-peer-review-zh`、`literature-review-organizer`）。
- 收尾建議下一步、點出可傳產物，不自動執行。完整鏈見 `../_shared/handoff.md`。

## 參考檔

- `references/evaluation-framework.md` — ScholarEval 八維度的品質指標、5 分制 rubric、評估檢核表、常見問題、建議權重與整體門檻。

## 出處

ScholarEval 框架：Moussa, H. N., Da Silva, P. Q., Adu-Ampratwum, D., East, A., Lu, Z., Puccetti, N., Xue, M., Sun, H., Majumder, B. P., & Kumar, S. (2025). *ScholarEval: Research Idea Evaluation Grounded in Literature*. arXiv:2510.16234. https://arxiv.org/abs/2510.16234
