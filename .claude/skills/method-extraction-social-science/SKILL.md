---
name: method-extraction-social-science
description: 針對社會科學相關領域的研究文件與檔案，進行實證研究方法提取與結構化分析，了解論文的研究設計、測量、資料收集和統計分析方法，特別適用於調查、實驗、準實驗、或混合方法研究。產生結構化輸出，語言為繁體中文，保留英文方法術語，並提供簡潔的方法解釋和基於證據的品質評估，方便使用者進行比較。本 skill 專攻單篇的「方法架構」。注意路由：若要跨多篇比較假設邏輯與支持狀態，改用 paper-research-logic-review；若要多篇綜整與研究缺口，改用 literature-review-organizer；若要單篇逐章精讀（非只抽方法），改用 paper-reading-zh。
version: 0.1.0
---

# 社科論文方法抽取（繁體中文）

> 遵守 Paperdoku 共用規範：`../_shared/anti_leakage.md`（以原文為準、禁記憶補完）、`../_shared/output_language.md`（繁中＋英文術語）。

## 任務定位

此 skill 用於抽取、整理與分析社會科學實證研究論文的方法結構。核心任務不是摘要研究發現，而是重建論文的方法邏輯：研究設計、樣本、操作化、量測品質、分析流程、推論邏輯與效度控制。以單篇論文為處理單位，輸出格式原生支援後續多篇跨篇比較。

## 適用 / 不適用範圍

**適用：** survey、longitudinal survey、experiment、quasi-experiment、archival/secondary data、panel data、multilevel study、mixed methods、qualitative coding with quantitative validation

**不適用：** 純質性研究、純理論文章、文獻回顧、方法論文章、非學術報告

## 核心原則

細節說明參照 `references/core-principles.md`

1. **不得臆測** — 無明確報告的資訊，標記為 not reported / unclear / inferred with low confidence（標記慣例見 `../_shared/confidence_language.md`；以原文為準見 `../_shared/anti_leakage.md`）
2. **三者不混淆** — 研究設計、量測設計、分析方法須明確區分
3. **方法與結果分離** — 顯著性、假說支持與否是結果，不是方法描述（見 `../_shared/hypothesis_support_discipline.md`）
4. **重建分析 pipeline** — 依流程順序完整抽取，不只列出主要方法名稱
5. **品質判讀有據可查** — 只依論文明確報告進行，不足則標示 reporting unclear
6. **輸出可比較** — 使用標準化 method labels 與固定欄位，參照 `references/normalized-method-labels.md`

## 執行流程

### 1. 取得檔案
接受上傳 PDF、本地資料夾路徑、DOI / arXiv / PubMed ID、論文網址、或雲端存儲（詢問資料夾名稱）。

### 2. 初步篩選
依 `../_shared/file_screening_rules.md`：無法讀取、非 PDF、非學術論文、超過 10MB 或小於 100KB，詢問使用者是否繼續；確認不處理則移入 `Unprocessed_Papers`。

### 3. 辨識方法類型（method family）
判斷主要類型（survey / longitudinal survey / experiment / quasi-experiment / archival / panel / multilevel / mixed methods），再標示次要元素。

### 4. 通用方法抽取
依 `references/extraction-schema.md` 的 A–J 欄位完整抽取。

### 5. 依研究類型補充
依 `references/type-specific-templates.md` 補充對應類型的專屬欄位。

### 6. 多研究論文
若含 Study 1、Study 2 等，依 `references/type-specific-templates.md` 第六節處理。

## 固定輸出順序

依 `references/output-schema-template.md` 格式輸出，順序如下：

1. 論文方法概覽表
2. 結構化抽取 schema（JSON-style）
3. comparison-ready 表格
4. 短篇方法解釋（方法邏輯摘要 / 品質判讀摘要 / 跨篇比較定位）
5. 品質判讀 — 依 `references/quality-assessment-rules.md`
6. 未報告 / 不清楚項目

## 檔案處理

完成後，若論文來自本地資料夾，先請求使用者同意，再將論文移入同資料夾的 `Readed_Papers`，輸出檔依 `../_shared/paper_naming_convention.md` 命名。無法辨識者移入 `Unprocessed_Papers` 並附上說明。（檔案篩選與資料夾慣例見 `../_shared/file_screening_rules.md`。）

## 風格要求

- 繁體中文為主，英文方法術語保留括號（見 `../_shared/output_language.md`）
- 優先使用表格與固定欄位
- 以可比較、可重複、可複核為優先
- 若附錄或補充材料有方法資訊，一併納入
- 若不同段落的方法描述彼此矛盾，明確指出

## 成功標準

成功的輸出應讓讀者可以：
1. 明確理解該論文如何進行資料分析
2. 直接與其他論文進行方法層次比較
3. 判斷該論文的方法報告是否完整且具可解釋性

## 上下游交接

- **產物**：方法架構結構化輸出寫成 markdown 存到 `reports/`（檔名沿用來源主幹＋`method`，見 `../_shared/paper_naming_convention.md`）。
- **上游**：PDF 先經 `source-document-extraction` 抽成 `extracted/*.md` 再讀。
- **下游**：輸出原生 comparison-ready，逐篇抽完可交 `literature-review-organizer` 綜整，或與 `paper-research-logic-review` 的假設邏輯互補。鏈見 `../_shared/handoff.md`。
