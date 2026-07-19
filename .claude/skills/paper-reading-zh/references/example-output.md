# 完整範例（示範語氣與結構）

針對一篇關於可解釋推薦系統的綜述論文，輸出大致長這樣。示範三部分的鋪陳、原文節錄的密度，以及結尾如何提醒論文類型並指向後續選項。

```markdown
## 各章節摘要

### I. Introduction（導論）
本章先回顧 XAI 的簡短歷史…（2–6 句）。
> 「These methods are essentially represented by black-boxes…」

### II. Recommender Systems Approaches（推薦系統方法）
系統性介紹六類推薦方法：
- **協同過濾（CF）**：根據歷史評分…分為 memory-based 與 model-based。
- **內容式**：…
…
> 「The CF systems work by collecting user's historical ratings information…」

## 整體分析

**研究目的**：提供以推薦系統為焦點的 XAI 結構化綜述…
**要解決的問題**：深度學習推薦模型是黑盒子，使用者無法理解「為什麼推薦了某項目」。
> 「…the problem of *why a certain recommendation was made?*」
**指出的研究缺口**：
1. 「解釋」缺乏統一定義…
> 「There is no agreement in scientific research on the definition of what an explanation is…」
2. 評估方法困難，尤其解釋品質需以人為中心…（作者明確列為最具挑戰的方向）
**整體結論**：XAI 導入推薦系統需跨領域協作；透明性是核心目標；評估是最大瓶頸。

## 初步的論文評論

**主要貢獻**：把 XAI 與推薦系統兩個領域的概念整理、分類並交會，對入門讀者是一張好地圖。
**證據與宣稱**：屬綜述／立場論文，沒有自己的實證資料，結論多為文獻歸納；作者也只把「實驗比較」列為未來工作，宣稱與定位相稱。
> 「As future work, we plan to conduct their experimental comparison…」
**疑點／張力**：對解釋品質的六項準則與七個目標多為羅列，較少批判彼此的取捨或衝突（我的觀察）。
**限制**：作者自陳最大挑戰在「評估需以人為中心」；此外全文未實作比較近年深度學習的可解釋方法。

> 提醒：這是一篇綜述／立場論文，沒有實證資料、假設或統計分析。若要針對某個宣稱回原文查證，可用本 skill 的 `claim-audit` 模式；若需要完整的批判性審查（逐條 Major／Minor comments 與修改建議），改用 `academic-peer-review-zh`。
```
