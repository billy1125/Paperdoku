# Skill 交接鏈（共用）

> Paperdoku suite 的交接正典。各 skill 以 `../_shared/handoff.md` 引用。定義 skill 之間如何傳遞產物，避免每個 skill 都從頭重讀。

## 誠實界線（先講清楚）

Claude Code **沒有自動 orchestrator** 連續跑多個 skill。這裡的「交接」= 三件事，不是自動串接：

1. **共用產物/目錄慣例**——下游 skill 知道去哪讀上游產物。
2. **每個 skill 自述上下游**——知道自己吃什麼、產什麼、接誰。**例外**：外部匯入（vendored）的 skill 為維持可攜性，其文件不含本專案的路徑與 skill 名，故不自述上下游，接線改寫在本檔（見「擷取層接線」節）。
3. **收尾建議下一步**——skill 做完主動建議下一個 skill 與可傳的產物，但**不自動執行**，由使用者決定。

## 兩條 pipeline

Paperdoku 分兩條可獨立運作、前後有關聯但不相依的 pipeline。前段在「動筆讀論文之前」找方向與定位，後段在「拿到論文之後」讀懂與整理，以**橋接點**相接但不共用產物資料夾、不自動串接。

## 前段交接鏈（研究設計 pipeline）

```
research-brainstorming-zh ──▶ paper-search ──▶ literature-scoping-zh ──▶ scholar-evaluation-zh ──▶ hypothesis-generation-zh
 (發散方向)                    (掌握文獻,共用)   (系統盤點/定缺口)          (關鍵文獻可信度)            (收斂研究問題)
      │                                              │                          │                          │
      └──── 產物一律寫到 research-design/<主題>-{brainstorm,scoping,credibility,hypotheses}.md ──────────────┘
                                                     │
                          【橋接點】前段挑出的關鍵論文 → 使用者放進 papers/ → 接後段擷取層
```

- 前段搜尋一律經 `paper-search`／MCP；`scholar-evaluation-zh`／`literature-scoping-zh` 要細評方法需先 `source-document-extraction` 抽全文。
- 前段共用紀律見 `research_design_discipline.md`。`hypothesis-generation-zh` 收斂出的研究問題，也可拿去後段 `literature-review-organizer` 的 systematic review 做正式回顧。

## 後段交接鏈（論文閱讀 pipeline）

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

## 擷取層接線（source-document-extraction 為外部匯入 skill）

`source-document-extraction` 是**外部匯入（vendored）**的技能：它遵循 Agent Skills 開放規格、刻意不綁定任何 repo，其 `SKILL.md`／`README.md`／`CLAUDE.md` 一律不寫本專案的路徑、目錄結構與其他 skill 名，因此**不自述上下游**。Paperdoku 的接線由本節定義：

- **上游**：使用者放進 `papers/` 的來源檔、`paper-search` 的候選（下載 PDF 後），或前段 `literature-scoping-zh`／`scholar-evaluation-zh` 挑出的關鍵論文（橋接點）。來源檔**保留不動**，只作對照與回溯。
- **下游**：產出 `extracted/<主幹>.md`，供後段閱讀/分析/審查層（`paper-reading-zh`、`method-extraction-social-science`、`paper-research-logic-review`、`academic-peer-review-zh`、`citation-verification-zh`、`literature-review-organizer`）直接 Read；前段兩個 skill 要細評方法時亦讀此產物。
- **輸出路徑：不要用 `-o`**。該 skill 的 `SKILL.md` 寫「若使用者的專案有既定的存放位置或檔名，用 `-o` 顯式指定」——Paperdoku 的既定位置正好等於它 `SDE_OUT_DIR` 的預設值 `extracted/`，維持預設即可；用 `-o` 把產物寫到別處會違反下面的交接鐵律第 1 條。
- **收尾建議下一步由代理補**（鐵律第 3 條）：該 skill 本身不會提示，抽完後由代理接一句「已抽成 `extracted/X.md`，要精讀可用 `paper-reading-zh`」。
- **更新方式**：整包覆蓋上游版本。**不要在該 skill 目錄內加回本專案的路徑或 skill 名**——下次覆蓋就會遺失；要調整接線改本節。

## 產物與目錄慣例

| 目錄 | 內容 | 產出者 | 消費者 |
|---|---|---|---|
| `papers/` | 未轉檔的來源文件（PDF/Word） | 使用者投放 | source-document-extraction（轉成 `extracted/*.md`） |
| `extracted/` | 抽取的論文全文 `.md`（檔名沿用來源主幹） | source-document-extraction | 所有閱讀/分析/審查 skill |
| `output/` | 搜尋清單、`references-*.bib` | paper-search | 使用者、可餵給分析層 |
| `Readed_Papers/` `Unprocessed_Papers/` | 已處理/未處理論文歸檔 | 分析層（需使用者同意） | — |
| `reports/` | 各 skill 的書面報告成果（markdown） | 所有閱讀/分析/審查 skill | 使用者、markdown-to-word（可轉 `.docx`） |
| `research-design/` | **前段** pipeline 產物（`<主題>-brainstorm/scoping/credibility/hypotheses.md`） | 前段 4 個 skill | 使用者、下游前段 skill、（橋接後）後段 |

（`papers/`、`extracted/`、`reports/`、`research-design/` 四個資料夾各以自帶的 `.gitignore`〔`*` + `!.gitignore`〕保留在版控、但**內容不進版控**；`output/` 與歸檔資料夾屬執行期產物。）

## 交接鐵律

1. **PDF 一律先經 `source-document-extraction` → 讀 `extracted/*.md`**，不對 PDF 直接動手（本機 Read 無法渲染 PDF）。這是全 suite 統一入口，避免各 skill 各自處理 PDF。
2. **不改上游產物、不重跑已完成階段**——已抽取的 `.md` 直接用；已搜尋的清單直接接。
3. **收尾建議下一步**：每個 skill 完成後，用一兩句建議自然的下一個 skill 並點出可傳的產物（如「已抽成 extracted/X.md，要精讀可用 paper-reading-zh」），但不自動執行。
4. **交接不繞過紀律**：跨 skill 傳遞不改變 `anti_leakage.md`——下游仍以原文為準，不因「上游說過」就當已驗證。

## 典型串法（使用者手動，skill 收尾提示）

- **從發想到研究問題（前段全程）**：research-brainstorming-zh（發散方向）→ paper-search（掌握文獻）→ literature-scoping-zh（盤點＋定缺口）→ scholar-evaluation-zh（篩查關鍵文獻可信度）→ hypothesis-generation-zh（收斂成可檢驗假設）。產物皆在 `research-design/`。
- **前段橋接到後段**：前段挑出必讀關鍵論文 → 使用者放進 `papers/` → source-document-extraction（抽）→ paper-reading-zh／literature-review-organizer（後段細讀或正式回顧）。
- **從一個主題到綜整**：paper-search（找）→ 下載 PDF → source-document-extraction（抽）→ literature-review-organizer（綜整，或 systematic review）。
- **讀懂並審一篇**：source-document-extraction（抽）→ paper-reading-zh（精讀）→ academic-peer-review-zh（審查）→ citation-verification-zh（查引用）。
- **報告交稿成 Word**：任一分析/審查 skill 寫出 `reports/*.md` →（要交稿或套期刊樣式）markdown-to-word 轉同主幹 `.docx`。
- **多篇方法比較**：source-document-extraction（逐篇抽）→ method-extraction-social-science（逐篇抽方法）→ 人工/organizer 比較。
