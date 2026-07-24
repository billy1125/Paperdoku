# 檢驗設計模式（experimental-design-patterns）

跨領域檢驗假設的設計模式。依假設性質選設計，並把控制、盲化、重複、混淆處理講清楚。社會科學研究亦適用（調查/實驗/準實驗/縱貫/多層次/混合方法）。

## 設計選擇框架

依以下選取徑：假設性質（機制/因果/相關/描述）、研究系統（in vitro／in vivo／計算／觀察）、可行性（時間/成本/倫理/技術）、所需證據（概念驗證/因果證明/量化關係）。

## 實驗室設計（in vitro／in vivo／計算）

- **Dose-Response（劑量反應）**：建立輸入與效果的量化關係；多劑量點＋陰性控制＋陽性控制＋技術重複（≥3）；曲線擬合、IC50/EC50。
- **Gain/Loss of Function（增益/失能）**：確立某成分的因果角色；野生型控制＋過表現＋敲除/抑制＋rescue 實驗。
- **Time-Course（時程）**：了解時間動態與事件順序；含基線與多時間點與充足重複。
- **Between-Subjects（受試者間）**：隨機分派不同組別接受不同處理；隨機、樣本量（檢定力分析）、控制組、盲化、條件標準化。
- **Within-Subjects／Repeated Measures（受試者內）**：每個受試者當自己的控制以降低個體間變異；基線、抗衡順序、washout、重複測量統計。
- **Factorial（因子設計）**：同時檢驗多因子與交互作用（如 2×2 genotype × treatment）；交互作用需足夠檢定力。
- **In Silico 模擬／Bioinformatics·Meta-Analysis**：以模型或既有大型資料檢驗；明確假設、參數敏感度、對已知資料驗證、多重檢定校正、獨立資料集驗證。

## 觀察研究設計（無法或不宜操弄時）

- **Cross-Sectional（橫斷）**：單一時點檢驗關聯；快、便宜、可估盛行率；**無法建立時序或因果**；需代表性抽樣與控制混淆。
- **Cohort／Longitudinal（世代/縱貫）**：追蹤群體、量測暴露與結果；可建立時序、算發生率；耗時、昂貴、流失；處理時變混淆。
- **Case-Control（病例對照）**：以結果分組回溯比較暴露；對罕見結果有效率；有回憶/選擇偏誤、無法算發生率。

## 臨床試驗設計

- **RCT（隨機對照試驗）**：人體介入的黃金標準；隨機、分派隱匿、盲化（受試者/施予者/評估者）、意向治療分析（ITT）、預先註冊協定與分析計畫。
- **Crossover（交叉試驗）**：每位受試者依序接受所有處理；降低個體間變異、需較少人；需足夠 washout、隨機順序、評估殘留效應；限可逆狀況。

## 進階考量

- **樣本量與檢定力**：先做正式檢定力分析；pilot 每組 n≥10；正式研究目標 ≥80% power；縱貫需計流失。
- **控制類型**：negative（無介入基線）／positive（已知有效，驗證系統）／vehicle（載體無活性成分）／sham（模擬介入無活性成分）／historical（最弱，盡量避免）。
- **盲化層級**：open-label／single-blind／double-blind／triple-blind（含分析者）。
- **重複**：technical replicates（同樣本重複測，2–3 次）／biological replicates（獨立樣本，n≥3、最好 5–10）／experimental replicates（整個實驗重跑，確認結果的黃金標準）。
- **混淆控制**：randomization／matching／blocking／統計調整／standardization。

## 依假設選設計（決策樹）

1. 變數可否操弄？可 → 實驗設計（RCT、實驗室實驗）；否 → 觀察設計（cohort、case-control、cross-sectional）。
2. 系統為何？細胞/分子 → in vitro；整個生物 → in vivo；人 → 臨床試驗或觀察；複雜系統 → 計算模型。
3. 主要目標？機制 → gain/loss、dose-response；因果 → RCT、good-control cohort；關聯 → cross-sectional、case-control；預測 → 建模/ML；時間動態 → time-course、縱貫。
4. 限制？時間 → cross-sectional、in vitro；預算 → 計算、觀察；倫理 → 觀察、in vitro；罕見結果 → case-control、meta-analysis。

## 整合多種取徑（三角驗證）

強的假設檢驗常結合多設計：觀察（關聯）→ 動物模型（因果操弄）→ in vitro（機制）→ RCT（人體介入）→ 計算（預測哪些條件應有效）。各設計處理不同面向與侷限；多取徑的收斂證據強化因果宣稱；通常從觀察/in vitro 起步，再推進到決定性的因果檢驗。**一個實驗鮮少能決定性檢驗一個假設**。

## 常見陷阱

樣本量不足（檢定力不夠）、缺適當控制、未處理混淆、統計檢定不當、p-hacking/多重檢定未校正、需主觀評估時缺盲化、未複製、（臨床）未預先註冊分析計畫。

## 實務要點

1. 設計對齊假設性質（因果宣稱需操弄；關聯可用觀察）。2. 先簡後繁（pilot 簡單設計再加複雜度）。3. 謹慎規劃控制以隔離特定效果並驗證系統。4. 權衡理想設計與現實限制。5. 預期需多個實驗。6. 預先指定統計檢定。7. 內建驗證（獨立複製、正交方法、收斂證據）。
