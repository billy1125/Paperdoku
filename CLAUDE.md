# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Paperdoku 是一套**研究設計與論文閱讀整理**的 Claude Code skill suite，分兩條 pipeline：

- **前段｜研究設計**：發想方向 → 掌握文獻 → 系統盤點/定缺口 → 檢驗關鍵文獻可信度 → 收斂研究問題。產物到 `research-design/`。
- **後段｜論文閱讀**：搜尋 → 擷取 → 閱讀/分析 → 綜整 → 匯出 Word。產物到 `reports/`。

兩段可獨立運作、前後有關聯但不相依，以橋接點相接（前段挑出的關鍵論文 → `papers/` → 後段擷取層），但不共用產物資料夾、不自動串接。

Suite 版本：0.1.0

## 這是什麼

- 產品本體是 `.claude/skills/` 下的 13 個 skill，外加 `_shared/` 共用規範。
- 不是一般應用程式專案：除 `source-document-extraction` 與 `markdown-to-word` 內含確定性 Python 腳本外，全為 prompt 驅動，沒有 build/lint/test 工具鏈。
- **可獨立抽離**：不依賴任何母 repo，整包搬走即可使用。
- `source-document-extraction` 是**外部匯入（vendored）**的 skill，其文件刻意不含本專案的路徑與 skill 名。接線寫在 `_shared/handoff.md`「擷取層接線」節；更新方式為整包覆蓋，別把本專案的路徑或 skill 名寫回該目錄。

## 路由紀律（先分類意圖，再分派）

收到需求時先分類，再依 `MODE_REGISTRY.md`（路由單一真相源）分派到唯一的 skill+mode。

**第 0 步：先分 pipeline，維持不混雜。** 動筆讀論文**之前**的需求走前段，**之後**的走後段。

| 前段：使用者想做的事 | skill |
|---|---|
| 發想研究方向 | `research-brainstorming-zh` |
| 掌握既有文獻 | `paper-search` |
| 系統盤點、定研究缺口 | `literature-scoping-zh` |
| 檢驗關鍵文獻可信度 | `scholar-evaluation-zh` |
| 收斂成可檢驗假設 | `hypothesis-generation-zh` |

後段（讀懂/審查/綜整手上的論文）依下列六點分派：

1. **明確指定** — 使用者點名 skill，或用單一明確觸發語（「精讀這篇」「多篇比較」「搜尋論文」「這份 PDF 讀不到」「發想研究方向」「收斂成假設」）→ 直接路由，不多問。
2. **單篇 vs 多篇** — 一篇、偏深入理解 → `paper-reading-zh`；多篇要比較 → 見第 3 點。
3. **兩個多篇 skill 分流** — 看**假設建構邏輯與支持狀態**（評估型，跳過方法細節）→ `paper-research-logic-review`；做**綜整/研究缺口/未來方向/回顧撰寫**（綜整型）→ `literature-review-organizer`。
4. **單篇的輕重階梯** — 輕量評論 → `paper-reading-zh` 的 `full`；查單一宣稱 → `claim-audit`；全篇多面向、下 Accept/Reject 判決的正式審查意見書 → `academic-peer-review-zh`。
5. **三種「查核」別混淆** — 某宣稱是否有原文證據 → `claim-audit`；參考文獻是否真實存在（揪幻覺引用）→ `citation-verification-zh`；研究是否有系統性偏誤 → `academic-peer-review-zh` 套 `_shared/risk_of_bias.md`。
6. **模糊素材先澄清** — 素材橫跨多階段又未點名意圖（如給一批 PDF ＋「幫我整理成回顧」），先問要哪一種產出，不憑素材長相硬猜。

兩組最容易走錯的界線：

- `literature-scoping-zh`（前段、吃 metadata、盤點定缺口）≠ `literature-review-organizer`（後段、吃全文、綜整寫作）
- `scholar-evaluation-zh`（可信度篩查、不判決）≠ `academic-peer-review-zh`（投稿審查、下判決）

## 基本操作流程

資料夾分工：

| 目錄 | 內容 |
|---|---|
| `papers/` | 未轉檔的來源文件（PDF/Word） |
| `extracted/` | 轉檔後的 `.md`，後段的閱讀來源 |
| `reports/` | 後段書面報告輸出 |
| `research-design/` | 前段產物（`<主題>-brainstorm`／`-scoping`／`-credibility`／`-hypotheses.md`） |
| `output/` | 搜尋清單與 BibTeX（沿用 `paper-search` 慣例，前後段共用） |

收到論文相關請求走以下三步：

1. **先確認意圖**：使用者只丟文件、或只說「幫我看一下」而未點名意圖時，**先列一份精簡意圖選單請他選**（精讀／快掃／方法萃取／多篇比較／審查／查引用），對照 `MODE_REGISTRY.md` 分派，不擅自預設。此步是路由紀律第 6 點的延伸。
2. **來源預設看 `papers/`**：動手前先確認對應的 `extracted/*.md` 是否已存在；**尚未轉檔就先用 `source-document-extraction` 轉**，不對 PDF 直接動手（見 `_shared/handoff.md` 交接鐵律）。輸出一律留在預設的 `extracted/`，**不要用 `-o`**。
3. **成果一律輸出到 `reports/`**：凡產出書面成果的 skill/模式，最終成品寫成 markdown 存進去（互動過程仍在對話）。檔名格式 `<來源論文主幹或主題>-<skill 或模式>.md`，主幹沿用 `_shared/paper_naming_convention.md`（例：`2024-Wang-Forecasting-peer-review.md`）；同名已存在先確認再覆寫。要交稿成 Word `.docx` 時用 `markdown-to-word`（只轉格式、不產內容；需 `pypandoc` ＋ pandoc）。

`papers/`、`extracted/`、`reports/`、`research-design/` 四個資料夾各以自帶的 `.gitignore`（`*` + `!.gitignore`）保留在版控、但**內容不進版控**；產出報告不必特別 `git add`。

## 關鍵規則

- **Anti-leakage（最高原則）**：只根據使用者提供的論文原文作答，禁止用模型記憶補完；不在原文的標記為未提及，不捏造。見 `_shared/anti_leakage.md`。
- **信心與缺漏**：依可讀程度調整語氣確定度，缺漏用標準標記不留白。見 `_shared/confidence_language.md`。
- **假設/方法紀律**：不從係數符號猜支持狀態、方法與結果分離。見 `_shared/hypothesis_support_discipline.md`。
- **輸出語言**：預設繁體中文、台灣用語，保留必要英文術語。見 `_shared/output_language.md`。
- **檔案處理**：任何檔案移動先徵得使用者同意。篩選與資料夾慣例見 `_shared/file_screening_rules.md`，命名見 `_shared/paper_naming_convention.md`。

## 共用規範（`.claude/skills/_shared/`）

各 skill 以相對路徑 `../_shared/<檔名>` 引用，不各自重寫。`_shared/` 無 SKILL.md，不會被當成 skill 載入。

| 檔案 | 內容 |
|---|---|
| `anti_leakage.md` | 以原文為準、禁記憶補完（最高鐵律） |
| `confidence_language.md` | 可讀層次、信心分級與語氣、缺漏標記 |
| `hypothesis_support_discipline.md` | 假設支持判定、方法/結果分離、三層次不混淆 |
| `file_screening_rules.md` | 檔案篩選門檻、Unprocessed/Readed 資料夾慣例 |
| `paper_naming_convention.md` | 處理後論文檔名規則 |
| `risk_of_bias.md` | 實證研究六面向 RoB 評估（peer-review 與 SR 模式共用） |
| `evidence_hierarchy.md` | 證據等級（meta > RCT > cohort…），跨篇綜整/衡量宣稱時加權 |
| `figure_fidelity.md` | 圖表查核：圖是否支撐 caption/宣稱（用 `--figures` 取圖 PNG，advisory） |
| `handoff.md` | skill 間交接鏈：產物/目錄慣例、交接鐵律、擷取層接線 |
| `output_language.md` | 輸出語言與術語慣例 |
| `research_design_discipline.md` | 前段共用紀律：提案非發現、主張分類標記、反缺口膨脹、三件事分離 |

## 環境與 MCP

以下是**每次運作都該知道**的守則；安裝與測試細節在 docs，平時不必載入。

- **Python 腳本一律走 `conda run -n research`**（`source-document-extraction` 與 `markdown-to-word` 共用此環境）。裸 `python`/`pip` 已於 `.claude/settings.json` `deny`，只 `allow` `conda run`／`conda create`／`conda install -n research ...`。
- **MCP 採專案層級**：根目錄 `.mcp.json`，兩個可用資料源 `semantic-scholar`（`uvx`）與 `openalex`（`npx`），可擇一或併用。金鑰／email 放在 gitignore 過的 `.claude/settings.local.json`，`.mcp.json` 以 `${VAR:-}` 引用；填改後需**重啟 session** 生效。
- **MCP 未連線時**，`citation-verification-zh` 誠實回報無法查核，**不憑記憶判定**（anti-leakage）。
- **改動任何 `SKILL.md` frontmatter 後必跑** `conda run -n research python tests/test_skill_frontmatter.py`（全過印 `ALL PASS`）：全形冒號 `：` 混進 key（如 `description：`）會讓整個 skill 靜默無法載入。
- **何時讀 docs**：只在第一次使用 `source-document-extraction`／`paper-search`／`citation-verification-zh`／`markdown-to-word`，或需重新安裝／測試時，才讀 [`docs/install.md`](docs/install.md) 與 [`docs/test.md`](docs/test.md)，並可**主動協助安裝與執行測試**。其餘情況不需載入。

## 已知邊界（本版）

- 交接**已文件化**（`_shared/handoff.md`）但**不是自動 orchestrator**——Claude Code 不會自動連跑多個 skill，靠共用目錄慣例、各 skill 自述上下游與收尾提示推進，由使用者決定下一步。（外部匯入的 `source-document-extraction` 不自述上下游，其接線寫在 `handoff.md`。）
- `academic-peer-review-zh` 只含學術論文審查路線；計畫書/補助案審查路線不在 Paperdoku 範圍。
