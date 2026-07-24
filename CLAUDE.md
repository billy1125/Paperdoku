# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

本檔提供 Claude Code 在此專案工作時的通用指引。Paperdoku 是一套**研究設計與論文閱讀整理**的 Claude Code skill suite，分兩條可獨立運作、前後有關聯但不相依的 pipeline：**研究設計 pipeline（前段）** 發想方向 → 掌握文獻 → 系統盤點/定缺口 → 檢驗關鍵文獻可信度 → 收斂研究問題；**論文閱讀 pipeline（後段）** 搜尋 → 擷取 → 閱讀/分析 → 綜整 → 匯出（Word）。

Suite 版本：0.1.0

## 這是什麼

- 產品本體是 `.claude/skills/` 下的 13 個 skill（多數 prompt 驅動），外加 `_shared/` 共用規範。
- 這不是一般應用程式專案；除 `source-document-extraction` 與 `markdown-to-word` 內含確定性 Python 腳本外，沒有 build/lint/test 工具鏈。
- 本專案設計為**可獨立抽離**：不依賴任何母 repo，整包搬走即可使用。

## 路由紀律（先分類意圖，再分派）

收到需求時，先分類，再依 `MODE_REGISTRY.md` 分派到唯一的 skill+mode:

0. **先分兩條 pipeline（最上層，維持不混雜）** — 動筆讀論文**之前**的需求（發想研究方向、找/盤點文獻、定研究缺口、檢驗關鍵文獻可信度、收斂研究問題）走**研究設計 pipeline（前段）**，產物到 `research-design/`：發散 → `research-brainstorming-zh`；掌握文獻 → `paper-search`；系統盤點/定缺口 → `literature-scoping-zh`；檢驗可信度 → `scholar-evaluation-zh`；收斂假設 → `hypothesis-generation-zh`。拿到論文**之後**的需求（讀懂/審查/綜整手上的論文）走**論文閱讀 pipeline（後段）**，見下列第 1–6 點，產物到 `reports/`。兩段用橋接點相接（前段挑出的關鍵論文 → `papers/` → 後段擷取層），但不共用產物資料夾、不自動串接。前段兩組易混淆界線：`literature-scoping-zh`（發現期盤點、吃 metadata）≠ `literature-review-organizer`（後段、吃全文綜整）；`scholar-evaluation-zh`（可信度篩查、不判決）≠ `academic-peer-review-zh`（投稿審查、下判決）。

1. **明確指定** — 使用者點名 skill 或用單一明確觸發語（如「精讀這篇」「多篇比較」「搜尋論文」「這份 PDF 讀不到」「發想研究方向」「收斂成假設」）：
   → 直接路由，不多問。

2. **單篇 vs 多篇** — 對象是**一篇**論文偏深入理解 → `paper-reading-zh`；對象是**多篇**要比較 → 多篇 skill（見下第 3 點分流）。

3. **兩個多篇 skill 分流**：
   - 要看**假設建構邏輯與支持狀態**（評估型，跳過方法細節）→ `paper-research-logic-review`
   - 要做**綜整/研究缺口/未來方向/文獻回顧撰寫**（綜整型）→ `literature-review-organizer`

4. **閱讀評論 vs 完整審查**（單篇的輕重階梯）：輕量評論用 `paper-reading-zh` 的 `full`；查單一宣稱用 `claim-audit`；要**全篇多面向、下 Accept/Reject 判決的正式審查意見書**用 `academic-peer-review-zh`。

5. **三種「查核」別混淆**：某宣稱是否有原文證據 → `paper-reading-zh` 的 `claim-audit`；參考文獻是否真實存在（揪幻覺引用）→ `citation-verification-zh`；研究是否有系統性偏誤 → `academic-peer-review-zh` 套 `_shared/risk_of_bias.md`。

6. **模糊/跨階段素材** — 素材橫跨多個階段又未點名意圖（如同時給一批 PDF + 要求「幫我整理成回顧」），**先澄清**要哪一種產出，不要憑素材長相硬猜路由。

完整模式對照見 `MODE_REGISTRY.md`（路由單一真相源）。

## 基本操作流程

資料夾分工：**後段** `papers/`（未轉檔的來源文件 PDF/Word）、`extracted/`（轉檔後的 `.md`、閱讀來源，既有慣例）、`reports/`（書面報告輸出）；**前段** `research-design/`（研究設計 pipeline 的產物：`<主題>-brainstorm.md`／`-scoping.md`／`-credibility.md`／`-hypotheses.md`）。前段搜尋產出的 BibTeX 仍沿用 `paper-search` 慣例寫到 `output/`。收到論文相關請求時走以下三步：

1. **先確認指令類型（意圖）**：使用者若只丟文件、或只說「幫我看一下」而未點名意圖，**先列一份精簡意圖選單請他選**（精讀 / 快掃 / 方法萃取 / 多篇比較 / 審查 / 查引用），對照 `MODE_REGISTRY.md` 分派，不擅自預設。此步是路由紀律第 6 點（模糊素材先澄清）的延伸。
2. **來源預設看 `papers/`**：論文來源檔放在 `papers/`。動手前先確認對應的 `extracted/*.md` 是否已存在——**若尚未轉檔，先用 `source-document-extraction` 把 `papers/` 的來源檔轉成 `extracted/*.md` 再讀**，不對 PDF 直接動手（見 `_shared/handoff.md` 交接鐵律）。
3. **成果一律輸出到 `reports/`**：凡產出書面成果的 skill/模式，最終成品直接寫成 markdown 存到 `reports/`（互動過程仍在對話）。檔名格式 `<來源論文主幹或主題>-<skill 或模式>.md`，來源主幹沿用 `_shared/paper_naming_convention.md`（例：`2024-Wang-Forecasting-peer-review.md`）；同名已存在先確認再覆寫。要把報告交稿成 Word `.docx` 時，用 `markdown-to-word`（終端匯出、只轉格式不產內容；需 `pypandoc`＋pandoc）。

`papers/`、`extracted/`、`reports/`、`research-design/` 四個資料夾各以自帶的 `.gitignore`（`*` + `!.gitignore`）保留在版控、但**內容不進版控**；產出報告不必特別 `git add`。

## 關鍵規則

- **Anti-leakage（最高原則）**：只根據使用者提供的論文原文作答，禁止用模型記憶補完論文內容；不在原文的標記為未提及，不捏造。完整鐵律見 `.claude/skills/_shared/anti_leakage.md`。
- **信心與缺漏**：依可讀程度調整語氣確定度，缺漏用標準標記不留白。見 `_shared/confidence_language.md`。
- **假設/方法紀律**：不從係數符號猜支持狀態、方法與結果分離。見 `_shared/hypothesis_support_discipline.md`。
- **輸出語言**：預設繁體中文、台灣用語，保留必要英文術語。見 `_shared/output_language.md`。
- **檔案處理**：任何檔案移動先徵得使用者同意；篩選與資料夾慣例見 `_shared/file_screening_rules.md`，命名見 `_shared/paper_naming_convention.md`。

## 共用規範(`.claude/skills/_shared/`)

各 skill 以相對路徑 `../_shared/<檔名>` 引用，不各自重寫：

| 檔案 | 內容 |
|---|---|
| `anti_leakage.md` | 以原文為準、禁記憶補完（最高鐵律） |
| `confidence_language.md` | 可讀層次、信心分級與語氣、缺漏標記 |
| `hypothesis_support_discipline.md` | 假設支持判定、方法/結果分離、三層次不混淆 |
| `file_screening_rules.md` | 檔案篩選門檻、Unprocessed/Readed 資料夾慣例 |
| `paper_naming_convention.md` | 處理後論文檔名規則 |
| `risk_of_bias.md` | 實證研究六面向 RoB 評估（peer-review 與 SR 模式共用） |
| `evidence_hierarchy.md` | 證據等級(meta>RCT>cohort…)，跨篇綜整/衡量宣稱時加權 |
| `figure_fidelity.md` | 圖表查核：圖是否支撐 caption/宣稱（用 --figures 取圖 PNG,advisory） |
| `handoff.md` | skill 間交接鏈：產物/目錄慣例、交接鐵律、收尾建議下一步 |
| `output_language.md` | 輸出語言與術語慣例 |
| `research_design_discipline.md` | 前段 pipeline 共用紀律：提案非發現、主張分類標記、anti-leakage 延伸、反缺口膨脹、三件事分離 |

`_shared/` 無 SKILL.md，不會被當成 skill 載入。

## 環境與 MCP（安裝/測試細節見 docs）

除 `source-document-extraction` 與 `markdown-to-word` 內含確定性 Python 腳本外，全 suite 皆 prompt 驅動、無 build/lint/test 工具鏈。以下是**每次運作都該知道**的守則；安裝、測試、常用指令等細節在 docs 與各 skill 的 `SKILL.md`，平時不必載入。

- `source-document-extraction` 與 `markdown-to-word` 的 Python 腳本一律走 `conda run -n research`（共用 `research` 環境；裸 `python`/`pip` 已於 `.claude/settings.json` `deny`，只 `allow` `conda run`／`conda create`／`conda install -n research ...`）。
- MCP 採**專案層級**：專案根目錄 `.mcp.json`，兩個可用資料源 `semantic-scholar`（`uvx`）與 `openalex`（`npx`），可擇一或併用；金鑰／email 放在 gitignore 過的 `.claude/settings.local.json`（`.mcp.json` 以 `${VAR:-}` 引用，不進版控），填改後需**重啟 session** 生效。MCP 未連線時 `citation-verification-zh` 誠實回報無法查核、**不憑記憶判定**（anti-leakage）。
- **改動任何 `SKILL.md` frontmatter 後**，跑 `conda run -n research python tests/test_skill_frontmatter.py`（全過印 `ALL PASS`）確認 YAML 仍可解析——全形冒號 `：` 混進 frontmatter 的 key（如 `description：`）會讓整個 skill 靜默無法載入。
- **僅在第一次使用 `source-document-extraction`／`paper-search`／`citation-verification-zh`／`markdown-to-word`，或需重新安裝／測試時才讀**：[`docs/install.md`](docs/install.md)（安裝指令與說明）、[`docs/test.md`](docs/test.md) ＋ `tests/test_mcp_servers.py`（測試指令與說明），並可**主動協助安裝與執行測試**（`conda run -n research python tests/test_mcp_servers.py`，全過印 `ALL PASS`）。其餘情況不需載入這些。

## 已知邊界（本版）

- skill 間交接**已文件化**（見 `_shared/handoff.md`）：共用 `extracted/`、`output/` 產物慣例 + 每個 skill 自述上下游 + 收尾建議下一步。**注意這不是自動 orchestrator**——Claude Code 不會自動連跑多個 skill，交接靠慣例與提示，由使用者推進。
- 完整同儕審查已內建(`academic-peer-review-zh`)，只含學術論文審查路線；計畫書/補助案審查路線不在 Paperdoku 範圍。
