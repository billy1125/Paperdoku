# Skill 交接鏈（共用）

> Paperdoku suite 的交接正典。各 skill 以 `../_shared/handoff.md` 引用。定義 skill 之間如何傳遞產物，避免每個 skill 都從頭重讀。

## 誠實界線（先講清楚）

Claude Code **沒有自動 orchestrator** 連續跑多個 skill。這裡的「交接」= 三件事，不是自動串接：

1. **共用產物/目錄慣例**——下游 skill 知道去哪讀上游產物。
2. **每個 skill 自述上下游**——知道自己吃什麼、產什麼、接誰。
3. **收尾建議下一步**——skill 做完主動建議下一個 skill 與可傳的產物，但**不自動執行**，由使用者決定。

## 交接鏈

```
paper-search ──清單/BibTeX──▶ source-document-extraction ──extracted/*.md──▶ 閱讀/分析/審查層 ──▶ literature-review-organizer ──▶ reports/*.md ──(選用)──▶ markdown-to-word
 (發現)                        (PDF→結構化 Markdown)          │ paper-reading-zh              (多篇綜整/SR)                             (Word .docx 交稿)
                                                              │ method-extraction-social-science
                                                              │ paper-research-logic-review
                                                              │ academic-peer-review-zh
                                                              │ citation-verification-zh
```

- **發現層**：`paper-search` 找候選、產清單與 BibTeX。
- **擷取層**：`source-document-extraction` 把 PDF/Word 轉成可讀的 `.md`（**全 suite 的 PDF 入口**）。
- **閱讀/分析/審查層**：讀 `extracted/*.md` 做精讀、方法萃取、邏輯審查、同儕審查、引用驗證。
- **綜整層**：`literature-review-organizer` 把多篇整理成綜整/研究缺口/系統性回顧。
- **匯出層（終端、選用）**：`markdown-to-word` 把 `reports/*.md` 轉成 Word `.docx`，供交稿或套期刊樣式範本；只轉格式、不產生內容。

## 產物與目錄慣例

| 目錄 | 內容 | 產出者 | 消費者 |
|---|---|---|---|
| `papers/` | 未轉檔的來源文件（PDF/Word） | 使用者投放 | source-document-extraction（轉成 `extracted/*.md`） |
| `extracted/` | 抽取的論文全文 `.md`（檔名沿用來源主幹） | source-document-extraction | 所有閱讀/分析/審查 skill |
| `output/` | 搜尋清單、`references-*.bib` | paper-search | 使用者、可餵給分析層 |
| `Readed_Papers/` `Unprocessed_Papers/` | 已處理/未處理論文歸檔 | 分析層（需使用者同意） | — |
| `reports/` | 各 skill 的書面報告成果（markdown） | 所有閱讀/分析/審查 skill | 使用者、markdown-to-word（可轉 `.docx`） |

（`papers/` 的 PDF/Word 來源受 `.gitignore` 的 `*.pdf`/`*.docx` 忽略；`reports/` 的 `.md` 會進版控；`extracted/`、`output/`、歸檔資料夾屬執行期產物。）

## 交接鐵律

1. **PDF 一律先經 `source-document-extraction` → 讀 `extracted/*.md`**，不對 PDF 直接動手（本機 Read 無法渲染 PDF）。這是全 suite 統一入口，避免各 skill 各自處理 PDF。
2. **不改上游產物、不重跑已完成階段**——已抽取的 `.md` 直接用；已搜尋的清單直接接。
3. **收尾建議下一步**：每個 skill 完成後，用一兩句建議自然的下一個 skill 並點出可傳的產物（如「已抽成 extracted/X.md，要精讀可用 paper-reading-zh」），但不自動執行。
4. **交接不繞過紀律**：跨 skill 傳遞不改變 `anti_leakage.md`——下游仍以原文為準，不因「上游說過」就當已驗證。

## 典型串法（使用者手動，skill 收尾提示）

- **從一個主題到綜整**：paper-search（找）→ 下載 PDF → source-document-extraction（抽）→ literature-review-organizer（綜整，或 systematic review）。
- **讀懂並審一篇**：source-document-extraction（抽）→ paper-reading-zh（精讀）→ academic-peer-review-zh（審查）→ citation-verification-zh（查引用）。
- **報告交稿成 Word**：任一分析/審查 skill 寫出 `reports/*.md` →（要交稿或套期刊樣式）markdown-to-word 轉同主幹 `.docx`。
- **多篇方法比較**：source-document-extraction（逐篇抽）→ method-extraction-social-science（逐篇抽方法）→ 人工/organizer 比較。
