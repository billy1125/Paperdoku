# Paperdoku — Mode Registry

> 全 suite 的路由單一真相源。使用者意圖 → 歸屬 skill → 模式。根目錄 `CLAUDE.md` 的路由紀律以本表為依據。新增/調整模式時，先改本表。

Suite 版本：0.1.0

## 兩條 pipeline（先分流，不混雜）

Paperdoku 分兩條可獨立運作、前後有關聯但不相依的 pipeline。先判斷意圖屬哪一條，再往下分派：

- **研究設計 pipeline（前段）**：動筆讀論文**之前**——找方向、找文獻、定缺口、檢驗關鍵文獻可信度、收斂研究問題。產物寫到 `research-design/`。
- **論文閱讀 pipeline（後段）**：拿到論文**之後**——擷取、精讀、方法/邏輯/同儕審查、引用查核、綜整、Word 匯出。產物寫到 `reports/`。

兩者以「橋接點」相接（前段挑出的關鍵論文 → `papers/` → 後段擷取層），但不自動串接、不共用產物資料夾。完整交接見 `.claude/skills/_shared/handoff.md`。

## 一、依意圖快速路由

### 研究設計 pipeline（前段）

| 使用者想做的事 | skill | 模式 |
|---|---|---|
| 發想研究方向、腦力激盪研究題目/機制 | `research-brainstorming-zh` | —（單一流程） |
| 在發現期把某主題文獻盤點成地圖、定研究缺口 | `literature-scoping-zh` | —（接 paper-search／MCP） |
| 檢驗關鍵文獻可信度/品質、給加權排序 | `scholar-evaluation-zh` | —（ScholarEval 八維度） |
| 把方向/現象收斂成可檢驗的假設與檢驗設計 | `hypothesis-generation-zh` | —（單一流程） |
| 掌握既有文獻（搜尋/追引用，前後段共用） | `paper-search` | —（單一流程） |

### 論文閱讀 pipeline（後段）

| 使用者想做的事 | skill | 模式 |
|---|---|---|
| 搜尋/查找某主題的論文、追引用 | `paper-search` | —（單一流程） |
| PDF/Word 讀不到，要先擷取成文字 | `source-document-extraction` | 依後端（見下） |
| 快速判斷一篇值不值得細讀 | `paper-reading-zh` | `quick-scan` |
| 精讀**單篇**、逐章摘要+輕量評論 | `paper-reading-zh` | `full`（預設） |
| 我想自己讀懂一篇，要人引導我思考 | `paper-reading-zh` | `socratic` |
| 查證某個宣稱在原文是否有證據支持 | `paper-reading-zh` | `claim-audit` |
| 查核一篇論文的參考文獻是否真實存在（揪幻覺引用） | `citation-verification-zh` | —（用 Semantic Scholar MCP） |
| 抽取**單篇**的研究方法架構（社科實證） | `method-extraction-social-science` | —（依方法族分支） |
| **多篇**比較：看假設邏輯與支持狀態 | `paper-research-logic-review` | 3 track（見下） |
| **多篇**綜整：研究缺口/未來方向/回顧撰寫 | `literature-review-organizer` | 4 目的 × 3 深度（見下） |
| 完整同儕審查（逐條 Major/Minor+Accept/Reject 判決） | `academic-peer-review-zh` | 依審查者風格（見下） |
| 把 `reports/` 的 markdown 報告匯出成 Word `.docx` | `markdown-to-word` | —（單一流程） |

## 二、各 skill 模式清單

### 前段 pipeline（研究設計，皆單一線性流程、prompt 驅動）
| skill | 做什麼 | 產物 |
|---|---|---|
| `research-brainstorming-zh` | 研究早期發散：產生/整理/挑戰/透明排序候選研究方向；主張分類標記、不自動選 winner | `research-design/<主題>-brainstorm.md` |
| `literature-scoping-zh` | 發現期系統盤點：搜尋策略→文獻地圖→主題群集→標定研究缺口（吃 paper-search／MCP metadata，未必有全文） | `research-design/<主題>-scoping.md` |
| `scholar-evaluation-zh` | 以 ScholarEval 八維度篩查已發表關鍵文獻可信度/品質、給 5 分制評分與加權排序（不下判決） | `research-design/<主題>-credibility.md` |
| `hypothesis-generation-zh` | 收斂：產生 3–5 競爭假設＋機制＋品質評估＋可檢驗預測＋檢驗設計 | `research-design/<主題>-hypotheses.md` |

- 共用紀律：`_shared/research_design_discipline.md`（提案非發現、主張分類標記、anti-leakage 延伸、反缺口膨脹、三件事分離）。
- 搜尋一律經 `paper-search`／MCP；`scholar-evaluation-zh`／`literature-scoping-zh` 細評需先 `source-document-extraction` 抽全文。

### paper-reading-zh（單篇閱讀，4 模式）
| 模式 | 用途 | 輕重 |
|---|---|---|
| `quick-scan` | WHY/HOW/WHAT 三段式快掃，判斷是否值得細讀 | 輕 |
| `full`（預設） | 逐章精讀 → 整體分析 → 初步評論 | 中 |
| `socratic` | 引導式提問，幫使用者自己讀懂；不直接給結論 | 中 |
| `claim-audit` | 針對特定宣稱回原文查證據相稱（引 `_shared/anti_leakage.md`） | 中 |

### paper-research-logic-review（多篇研究邏輯，3 track）
| track | 輸出 |
|---|---|
| 支持狀態快速彙整 | 論文總結表 + 每篇支持/不支持清單 |
| 假設邏輯完整審查（預設） | 上者 + 單篇邏輯品質註釋 + 批量綜合 |
| 研究架構深度分析 | 上者 + 變數關係 + 理論貢獻 + 跨論文模式 |

### literature-review-organizer（多篇綜整）
- 目的：研究缺口分析 / 研究方向探索 / 文獻回顧撰寫 / 主題快速掌握
- 深度：`quick scan` / `standard review`（預設） / `deep review` / **`systematic review`**（PRISMA 流程 + 納入排除 + 逐篇 RoB，見該 skill `references/mode-systematic-review.md`）

### citation-verification-zh（引用存在性驗證）
- 逐條查核一篇論文/一份參考文獻清單的引用**是否真實存在**，透過 Semantic Scholar 比對，揪出可能的幻覺引用或引錯文獻。
- 四態：✅找到 / ⚠️查無 / 🔶資訊不足 / ⛔無法查核（MCP 降級）；查無附污染風險 advisory。
- **前置**：需 `semantic-scholar` MCP（與 `paper-search` 共用）。
- 與 `claim-audit` 的差別：本 skill 查「引用**是否存在**」；`claim-audit` 查「引用/證據**是否支持某宣稱**」——兩件事。

### method-extraction-social-science（單篇方法萃取）
- 無使用者選 mode；依偵測到的**方法族**(survey / experiment / quasi-experiment / longitudinal-panel / multilevel / mixed methods)套專屬補充欄位。
- 適用：社科實證論文。不適用：純質性、純理論、文獻回顧、方法論文章、非學術報告。

### source-document-extraction（文件擷取）
- PDF 後端：`pymupdf4llm`（預設）/ `--legacy`（自製後端）；旁路：`--raw` / `--outline` / `--pages`。
- **`--figures`**：把選定頁 render 成 PNG（供 VLM 圖表查核，見 `_shared/figure_fidelity.md`）。
- Word:mammoth（預設）/ `--txt`。

### academic-peer-review-zh（完整同儕審查）
- 為**單篇**論文產出繁中審查意見書：摘述 → 整體評估 → 逐條 Major/Minor（問題→證據→修改方向） → **總體建議(Accept / Minor Revision / Major Revision / Reject)**。
- 支援論文型態：量化（SEM/PLS-SEM/迴歸）、實驗/準實驗、質性、混合方法。
- 模式：**預設單一審查者**（可設風格：嚴格/中立/發展） / **`panel`**（多視角面板 + 主編綜合） / **`calibration`**（對 gold set 量 FNR/FPR）。
- 實證論文可套 `_shared/risk_of_bias.md`（六面向 RoB）；結論強度對照 `_shared/evidence_hierarchy.md`。
- 與 `paper-reading-zh` 的輕重階梯：`full`（輕量評論，不判決） → `claim-audit`（單一宣稱查核） → `academic-peer-review-zh`（全篇、多面向、下判決）。

### paper-search（論文搜尋）
- 單一線性流程，透過 Semantic Scholar MCP。無 mode。

### markdown-to-word（報告匯出 Word）
- 單一線性流程、無 mode：把 `reports/` 的 markdown 報告以 Pandoc（`pypandoc`）轉成 Word `.docx`，GFM 表格轉為 Word 原生表格。
- 選項：`--reference-doc` 套期刊樣式範本、`--make-reference` 產生可編輯的樣式範本。
- **前置**：conda 環境 `research` ＋ `pypandoc` ＋ conda-forge `pandoc`（見 `docs/install.md` 第 5 節）。
- **終端匯出層**：只轉格式、不產生內容；上游為任何寫出 `reports/*.md` 的 skill。

## 三、邊界釐清（易混淆處）

- **前段 vs 後段（最上層）**：找方向/找文獻/定缺口/檢驗可信度/收斂研究問題 = 前段（產物 `research-design/`）；讀懂/審查/綜整手上的論文 = 後段（產物 `reports/`）。素材橫跨兩段又未點名意圖時，先澄清要哪一段的產出。
- **`literature-scoping-zh` vs `literature-review-organizer`**：前者在**發現期**、吃 `paper-search`／MCP metadata（未必有全文），輸出「盤點＋缺口地圖」定研究方向；後者在**後段**、吃 `extracted/*.md` 全文，做綜整寫作與完整 PRISMA systematic review 與逐篇 RoB。
- **`scholar-evaluation-zh` vs `academic-peer-review-zh`**：前者是**發現期**對「別人已發表關鍵文獻」做可信度篩查/加權、**不下判決**；後者對「一篇投稿」產出完整審查意見書並下 Accept/Minor/Major/Reject。
- **單篇 vs 多篇**：`paper-reading-zh`（單篇、敘事式深讀）vs `paper-research-logic-review`/`literature-review-organizer`（多篇、表格式）。
- **兩個多篇 skill**:`paper-research-logic-review` = **評估型**（假設建構邏輯與支持狀態，刻意跳過方法/抽樣/統計細節）；`literature-review-organizer` = **綜整型**（比較、研究缺口、未來方向、文獻回顧草稿）。要逐假設評邏輯用前者，要綜整寫回顧用後者。
- **方法焦點**：`paper-research-logic-review` 跳過方法；`method-extraction-social-science` 專攻方法架構——兩者為互補的兩半。
- **搜尋 vs 綜整**：`paper-search` 只負責找與列清單；深度比較分析交給多篇 skill。
- **閱讀評論 vs 完整審查**：`paper-reading-zh` 的 `full` 是輕量評論（不判決）、`claim-audit` 是單一宣稱查核；要全篇、多面向、下 Accept/Reject 判決，用 `academic-peer-review-zh`。
- **各種「查核」別混淆**：`claim-audit`=某宣稱是否有原文證據；`citation-verification-zh`=參考文獻是否真實存在；`academic-peer-review-zh` 的 RoB=研究是否有系統性偏誤；`figure_fidelity`=圖是否支撐 caption/宣稱。

## 四、範圍說明

- **完整同儕審查已內建**（`academic-peer-review-zh`，只含學術論文審查路線；計畫書/補助案審查路線不在 Paperdoku 範圍）。
- **交接鏈已文件化**(`_shared/handoff.md`):search→extract→read/analyze→organize 的產物/目錄慣例與收尾提示。非自動 orchestrator——由使用者推進，skill 只在收尾建議下一步。
