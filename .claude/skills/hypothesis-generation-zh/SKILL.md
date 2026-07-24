---
name: hypothesis-generation-zh
description: 研究設計 pipeline（前段）的收斂步——把研究方向與既有證據收斂成可檢驗的研究問題與假設：從觀察/現象出發，產生 3–5 個競爭假設、附機制解釋、評估假設品質（testability／falsifiability／parsimony／explanatory power／scope／consistency／novelty）、提出可檢驗預測與檢驗設計。當使用者要「把方向收斂成可檢驗的假設」「幫我從這個現象發展假設」「這個觀察有哪些競爭解釋、怎麼檢驗」「幫我把研究問題明確化成 H1/H2」「設計實驗來驗證這個想法」時使用。輸出繁體中文，產物寫到 research-design/<主題>-hypotheses.md；要精美 Word 交給 markdown-to-word。注意路由：本 skill 做「收斂成假設＋檢驗設計」；開放式發散找方向改用 research-brainstorming-zh；掌握既有文獻改用 paper-search；系統盤點與定缺口改用 literature-scoping-zh；評估關鍵文獻可信度改用 scholar-evaluation-zh。要對「手上已有的論文」看它自己的假設建構邏輯與支持狀態屬後段 pipeline 的 paper-research-logic-review。兩條 pipeline 不混用。
version: 0.1.0
---

# 假設生成技能（Hypothesis Generation）

研究設計 pipeline（前段）的**收斂終點**。用途是把前段累積的方向與證據，收斂成一組**可檢驗的研究問題與競爭假設**，附機制、品質評估、可檢驗預測與檢驗設計。產出是提案：**發想與設計，不是驗證**——驗證需要實際觀察與獨立檢驗。遵守 `../_shared/research_design_discipline.md`、`../_shared/anti_leakage.md`、`../_shared/hypothesis_support_discipline.md`（假設/方法/結果分離、不從係數符號猜支持）、`../_shared/output_language.md`、`../_shared/confidence_language.md`、`../_shared/evidence_hierarchy.md`。

## 適用情境

- 「把這個方向/現象收斂成可檢驗的假設（H1、H2…）」
- 「這個觀察有哪些競爭解釋？怎麼設計實驗區分它們？」
- 「幫我把研究問題明確化，並提出可檢驗預測」

不適用（請改路由）：開放式發散找方向 → `research-brainstorming-zh`；找文獻 → `paper-search`；盤點與定缺口 → `literature-scoping-zh`；評關鍵文獻可信度 → `scholar-evaluation-zh`；看「手上論文自己的」假設邏輯與支持狀態 → 後段 `paper-research-logic-review`。

## 工作流程

### 1. 理解現象

界定需要解釋的核心觀察或模式：範圍與邊界、限制與情境、已知 vs 不確定、相關領域。

### 2. 文獻查證（接 paper-search／MCP）

透過 `paper-search` 查既有證據為假設奠基：相似現象、相關機制、類比系統、既有理論、未解爭論與矛盾發現。**任何文獻宣稱只能來自 MCP 回傳或使用者提供原文，禁止憑記憶捏造**（anti-leakage）。記錄搜尋邊界，避免把「沒查到」當缺口。

### 3. 綜整既有證據

摘述目前對現象的理解、可能適用的既有機制、衝突證據、缺口、來自相關系統的類比。跨篇衡量證據強弱用 `../_shared/evidence_hierarchy.md`。

### 4. 產生競爭假設（3–5 個）

每個假設須：提供**機制解釋**（不只描述）、彼此可區分、扎根於證據綜整、考慮不同解釋層級（如社會/組織/個人/認知，或分子/細胞/系統/群體）。手法（套用類比系統的已知機制、多重因果路徑、不同尺度、質疑既有假設、新穎組合）見 `references/hypothesis-quality-criteria.md`。

### 5. 評估假設品質

依 `references/hypothesis-quality-criteria.md` 七準則逐一評估並明講強弱：testability（可檢驗）、falsifiability（可否證）、parsimony（簡約）、explanatory power（解釋力）、scope（範圍）、consistency（與既有知識一致）、novelty（新穎與洞見）。避免 just-so story、內建逃生條款的不可否證假設、無必要的過度複雜。

### 6. 設計檢驗

為每個可行假設提出具體檢驗設計，見 `references/experimental-design-patterns.md`：測什麼、需要哪些比較/控制、用什麼方法、樣本量/統計取徑、可能的混淆與如何處理。涵蓋實驗（in vitro／in vivo／計算）、觀察（cross-sectional／cohort／case-control）、（適用時）臨床試驗或準實驗/自然實驗。社會科學研究亦適用調查/實驗/準實驗/縱貫/混合設計。

### 7. 形成可檢驗預測

為每個假設給具體、盡量量化的預測：若假設成立應觀察到什麼、預期方向與量級、成立條件、**與競爭假設的區分性預測**、什麼觀察會否證它。

### 8. 結構化輸出

彙整成 markdown 報告（見下）。**保持假設/方法/結果分離**：假設是待驗證的命題，檢驗設計是方法，兩者都不等於已得到支持。

## 輸出格式（產物）

寫成 markdown 存到 `research-design/<主題>-hypotheses.md`（要精美 Word 版交給 `markdown-to-word`）：

1. **現象界定**（核心觀察、範圍、已知/不確定）
2. **證據綜整**（接 paper-search，含搜尋邊界與證據等級）
3. **競爭假設**（H1–H5，每個：機制解釋＋關鍵支持證據＋核心假設前提）
4. **假設品質評估表**：| 假設 | testability | falsifiability | parsimony | explanatory power | scope | consistency | novelty | 綜合註記 |
5. **可檢驗預測**（每假設，含區分性預測）
6. **檢驗設計**（每假設的關鍵取徑；細節如控制/樣本量/統計可另立段落）
7. **關鍵比較**（哪個實驗最能有效區分競爭假設）
8. **建議下一步**

## 上下游交接

- **上游**：`research-brainstorming-zh`（方向）、`literature-scoping-zh`（缺口）、`scholar-evaluation-zh`（加權後的可信證據）、`paper-search`（文獻）。
- **下游（橋接到後段）**：收斂出的研究問題/假設 → 可拿去後段 `literature-review-organizer` 的 systematic review 做正式文獻回顧，或指引實際研究執行；要看某既有論文自己的假設支持邏輯 → 後段 `paper-research-logic-review`。
- 收尾建議下一步、點出可傳產物，不自動執行。完整鏈見 `../_shared/handoff.md`。

## 參考檔

- `references/hypothesis-quality-criteria.md` — 七項假設品質準則（testability／falsifiability／parsimony／explanatory power／scope／consistency／novelty）、競爭假設比較與區分性、常見陷阱。
- `references/experimental-design-patterns.md` — 跨領域檢驗設計模式（實驗室、觀察研究、臨床試驗、計算模型）、控制/盲化/重複/混淆處理、依假設選設計的決策樹。
