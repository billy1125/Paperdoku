# CLAUDE.md — Paperdoku

本檔提供 Claude Code 在此專案工作時的通用指引。Paperdoku 是一套**論文閱讀與文獻整理**的 Claude Code skill suite,涵蓋:搜尋 → 擷取 → 閱讀/分析 → 綜整。

Suite 版本:0.1.0

## 這是什麼

- 產品本體是 `.claude/skills/` 下的 6 個 skill(prompt 驅動),外加 `_shared/` 共用規範。
- 這不是一般應用程式專案;除 `source-document-extraction` 內含確定性 Python 腳本外,沒有 build/lint/test 工具鏈。
- 本專案設計為**可獨立抽離**:不依賴任何母 repo,整包搬走即可使用。

## 路由紀律(先分類意圖,再分派)

收到需求時,先分類,再依 `MODE_REGISTRY.md` 分派到唯一的 skill+mode:

1. **明確指定** — 使用者點名 skill 或用單一明確觸發語(如「精讀這篇」「多篇比較」「搜尋論文」「這份 PDF 讀不到」):
   → 直接路由,不多問。

2. **單篇 vs 多篇** — 對象是**一篇**論文偏深入理解 → `paper-reading-zh`;對象是**多篇**要比較 → 多篇 skill(見下第 3 點分流)。

3. **兩個多篇 skill 分流**:
   - 要看**假設建構邏輯與支持狀態**(評估型,跳過方法細節)→ `paper-research-logic-review`
   - 要做**綜整/研究缺口/未來方向/文獻回顧撰寫**(綜整型)→ `literature-review-organizer`

4. **閱讀評論 vs 完整審查**(單篇的輕重階梯):輕量評論用 `paper-reading-zh` 的 `full`;查單一宣稱用 `claim-audit`;要**全篇多面向、下 Accept/Reject 判決的正式審查意見書**用 `academic-peer-review-zh`。

5. **三種「查核」別混淆**:某宣稱是否有原文證據 → `paper-reading-zh` 的 `claim-audit`;參考文獻是否真實存在(揪幻覺引用)→ `citation-verification-zh`;研究是否有系統性偏誤 → `academic-peer-review-zh` 套 `_shared/risk_of_bias.md`。

6. **模糊/跨階段素材** — 素材橫跨多個階段又未點名意圖(如同時給一批 PDF + 要求「幫我整理成回顧」),**先澄清**要哪一種產出,不要憑素材長相硬猜路由。

完整模式對照見 `MODE_REGISTRY.md`(路由單一真相源)。

## 關鍵規則

- **Anti-leakage(最高原則)**:只根據使用者提供的論文原文作答,禁止用模型記憶補完論文內容;不在原文的標記為未提及,不捏造。完整鐵律見 `.claude/skills/_shared/anti_leakage.md`。
- **信心與缺漏**:依可讀程度調整語氣確定度,缺漏用標準標記不留白。見 `_shared/confidence_language.md`。
- **假設/方法紀律**:不從係數符號猜支持狀態、方法與結果分離。見 `_shared/hypothesis_support_discipline.md`。
- **輸出語言**:預設繁體中文、台灣用語,保留必要英文術語。見 `_shared/output_language.md`。
- **檔案處理**:任何檔案移動先徵得使用者同意;篩選與資料夾慣例見 `_shared/file_screening_rules.md`,命名見 `_shared/paper_naming_convention.md`。

## 共用規範(`.claude/skills/_shared/`)

各 skill 以相對路徑 `../_shared/<檔名>` 引用,不各自重寫:

| 檔案 | 內容 |
|---|---|
| `anti_leakage.md` | 以原文為準、禁記憶補完(最高鐵律) |
| `confidence_language.md` | 可讀層次、信心分級與語氣、缺漏標記 |
| `hypothesis_support_discipline.md` | 假設支持判定、方法/結果分離、三層次不混淆 |
| `file_screening_rules.md` | 檔案篩選門檻、Unprocessed/Readed 資料夾慣例 |
| `paper_naming_convention.md` | 處理後論文檔名規則 |
| `risk_of_bias.md` | 實證研究六面向 RoB 評估(peer-review 與 SR 模式共用) |
| `evidence_hierarchy.md` | 證據等級(meta>RCT>cohort…),跨篇綜整/衡量宣稱時加權 |
| `figure_fidelity.md` | 圖表查核:圖是否支撐 caption/宣稱(用 --figures 取圖 PNG,advisory) |
| `handoff.md` | skill 間交接鏈:產物/目錄慣例、交接鐵律、收尾建議下一步 |
| `output_language.md` | 輸出語言與術語慣例 |

`_shared/` 無 SKILL.md,不會被當成 skill 載入。

## 執行環境(僅 source-document-extraction 需要)

- 該 skill 的 Python 腳本一律在 conda 環境 `research`(Python 3.11)執行:`conda run -n research python ...`。
- **不直接呼叫裸 `python`/`pip`**(已於 `.claude/settings.json` 封鎖);安裝與指令見該 skill 的 `SKILL.md` / `CLAUDE.md`。

## 已知邊界(本版)

- skill 間交接**已文件化**(見 `_shared/handoff.md`):共用 `extracted/`、`output/` 產物慣例 + 每個 skill 自述上下游 + 收尾建議下一步。**注意這不是自動 orchestrator**——Claude Code 不會自動連跑多個 skill,交接靠慣例與提示,由使用者推進。
- 完整同儕審查已內建(`academic-peer-review-zh`),只含學術論文審查路線;計畫書/補助案審查路線不在 Paperdoku 範圍。
