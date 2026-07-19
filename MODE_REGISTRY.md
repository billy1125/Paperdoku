# Paperdoku — Mode Registry

> 全 suite 的路由單一真相源。使用者意圖 → 歸屬 skill → 模式。根目錄 `CLAUDE.md` 的路由紀律以本表為依據。新增/調整模式時，先改本表。

Suite 版本：0.1.0

## 一、依意圖快速路由

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

## 二、各 skill 模式清單

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

## 三、邊界釐清（易混淆處）

- **單篇 vs 多篇**：`paper-reading-zh`（單篇、敘事式深讀）vs `paper-research-logic-review`/`literature-review-organizer`（多篇、表格式）。
- **兩個多篇 skill**:`paper-research-logic-review` = **評估型**（假設建構邏輯與支持狀態，刻意跳過方法/抽樣/統計細節）；`literature-review-organizer` = **綜整型**（比較、研究缺口、未來方向、文獻回顧草稿）。要逐假設評邏輯用前者，要綜整寫回顧用後者。
- **方法焦點**：`paper-research-logic-review` 跳過方法；`method-extraction-social-science` 專攻方法架構——兩者為互補的兩半。
- **搜尋 vs 綜整**：`paper-search` 只負責找與列清單；深度比較分析交給多篇 skill。
- **閱讀評論 vs 完整審查**：`paper-reading-zh` 的 `full` 是輕量評論（不判決）、`claim-audit` 是單一宣稱查核；要全篇、多面向、下 Accept/Reject 判決，用 `academic-peer-review-zh`。
- **各種「查核」別混淆**：`claim-audit`=某宣稱是否有原文證據；`citation-verification-zh`=參考文獻是否真實存在；`academic-peer-review-zh` 的 RoB=研究是否有系統性偏誤；`figure_fidelity`=圖是否支撐 caption/宣稱。

## 四、範圍說明

- **完整同儕審查已內建**（`academic-peer-review-zh`，只含學術論文審查路線；計畫書/補助案審查路線不在 Paperdoku 範圍）。
- **交接鏈已文件化**(`_shared/handoff.md`):search→extract→read/analyze→organize 的產物/目錄慣例與收尾提示。非自動 orchestrator——由使用者推進，skill 只在收尾建議下一步。
