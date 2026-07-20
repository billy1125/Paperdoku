# Paperdoku

一套用於**論文閱讀與文獻整理**的 Claude Code skill suite，涵蓋從搜尋、擷取、精讀到多篇綜整的工作流。繁體中文優先，設計哲學參考 human-in-the-loop 的學術研究工具（如 Academic Research Skills）：**AI 是副駕駛，幫你處理精讀、比較、查證的粗活，判斷與詮釋仍由你來。**

Suite 版本：0.1.0

## ⚠️ 免責聲明與使用須知 / Disclaimer

> **使用前請先閱讀。使用本專案即代表你接受以下條款。**

- **功能範圍**：Paperdoku 協助論文的搜尋、擷取、閱讀、方法抽取、邏輯與同儕審查、引用查核與文獻綜整。所有摘要、評論、評分與判決都是**輔助性質**，不取代你自己的專業判斷。
- **以原文為準，不憑記憶**：各 skill 遵守 anti-leakage 鐵律，只根據你提供的原文作答；但 AI 仍可能誤讀、遺漏或過度推論，**採用任何結論前請自行核對原文**。
- **側專案性質**：這是個人研究與測試性質的側專案，內容大量與 AI 共創，測試尚未完整，可能含錯誤或 bug，並非正式、穩定或已完整驗證的產品。
- **不保證正確**：AI 的閱讀摘要、審查意見、方法判讀，以及來自 Semantic Scholar 的引用查核結果（找到／查無／資訊不足）**不保證正確或完整**。引用查核尤其只是 advisory 風險訊號——「查無」不等於引用一定是假的（可能只是未被索引）。一切採用前請自行查證。
- **學術誠信**：AI 的產出僅供輔助，作者對最終文稿、研究宣稱、資料與投稿內容負完全責任，並須遵守所屬機構與期刊的誠信規範。
- **著作權與素材**：放入 `papers/` 的第三方期刊論文須為**合法取得**，僅供個人研究閱讀與分析之用，不得違反出版商服務條款。轉檔產物（`extracted/`）與報告（`reports/`）請自行妥善保管。
- **風險自負 / Use at your own risk.**

## 技能一覽

| Skill | 做什麼 | 模式 |
|---|---|---|
| `paper-reading-zh` | **單篇**論文深入閱讀 | quick-scan / full（預設） / socratic / claim-audit |
| `academic-peer-review-zh` | **單篇**完整同儕審查（下 Accept/Reject 判決；含 RoB、證據等級） | 單一（嚴格/中立/發展） / panel / calibration |
| `citation-verification-zh` | 查核參考文獻**是否真實存在**（揪幻覺引用） | 用 Semantic Scholar MCP |
| `paper-research-logic-review` | **多篇**研究邏輯審查（假設建構與支持狀態） | 3 track |
| `literature-review-organizer` | **多篇**綜整（比較表/缺口/未來方向/回顧；含 PRISMA） | 4 目的 × 4 深度（含 systematic review） |
| `method-extraction-social-science` | **單篇**社科實證方法架構萃取 | 依方法族分支 |
| `paper-search` | 透過 Semantic Scholar 搜尋論文、追引用 | 單一流程 |
| `source-document-extraction` | PDF/Word → 結構化 Markdown;`--figures` 出圖 PNG | 多後端 |

完整的模式對照與路由見 [`MODE_REGISTRY.md`](MODE_REGISTRY.md)；工作方式與規則見 [`CLAUDE.md`](CLAUDE.md)。

## 快速開始

安裝為專案技能後（skills 位於 `.claude/skills/`,Claude Code 會自動辨識），直接用自然語言或斜線指令觸發：

```text
精讀這篇論文                      → paper-reading-zh (full)
快速掃一下這篇值不值得讀           → paper-reading-zh (quick-scan)
幫我審這篇投稿論文、給修改意見       → academic-peer-review-zh
查一下這篇的參考文獻是不是真的       → citation-verification-zh
幫我比較這幾篇的假設邏輯           → paper-research-logic-review
把這批文獻整理成研究缺口           → literature-review-organizer
用 PRISMA 做一份系統性回顧          → literature-review-organizer (systematic review)
抽取這篇的研究方法                → method-extraction-social-science
搜尋「AI in education」相關論文     → paper-search
這份 PDF 讀不到,先擷取成文字       → source-document-extraction
```

## 基本使用流程

1. 把論文（PDF/Word）放進 `papers/`。
2. 下指令說要做什麼（精讀、審查、比較……）；沒給指令時，Claude 會列一份意圖選單請你選。
3. 論文若還沒轉成文字，Claude 會先用 `source-document-extraction` 把 `papers/` 的來源檔轉成 `extracted/*.md` 再讀。
4. 分析與審查的書面報告會直接以 markdown 輸出到 `reports/`。

## 前置需求

完整安裝步驟見 [`docs/install.md`](docs/install.md)。外部相依只集中在兩個 skill；其餘 5 個閱讀/分析 skill 為 prompt 驅動，**不需任何外部安裝**。

- **Claude Code**（最新版）——執行整個 suite 的平台。
- **paper-search 與 citation-verification-zh**：有兩個可用資料源 MCP，可擇一或併用——**Semantic Scholar**（需 `uv`／`uvx` + `git`）與 **OpenAlex**（需 Node.js，`npx` 啟動）。金鑰／email 皆選用（免費）。
- **source-document-extraction**：需 conda 環境 `research`(Python 3.11)與 `pymupdf`／`pdfplumber`／`pymupdf4llm`／`python-docx`／`mammoth`；裸 `python`/`pip` 已封鎖，一律走 `conda run -n research`。

## 設計要點

- **共用規範集中**：反捏造(anti-leakage)、信心分級、假設支持紀律等收在 `.claude/skills/_shared/`，各 skill 引用而非各自重寫。
- **路由單一真相源**：所有模式與分流集中在 `MODE_REGISTRY.md`。
- **可獨立抽離**：不依賴任何母 repo，整個 `Paperdoku/` 目錄可作為獨立專案搬走使用。

## 目錄結構

```
Paperdoku/
  CLAUDE.md            工作方式 + 路由紀律
  README.md            本檔
  MODE_REGISTRY.md     模式 → skill 路由表
  docs/
    install.md         安裝與前置需求（外部相依集中處）
    test.md            MCP 連線測試的指令與說明
  tests/
    test_mcp_servers.py  兩個資料源 MCP 的連線測試（conda run 執行）
  papers/              放未轉檔的來源文件（PDF/Word）
  reports/             分析/審查報告的 markdown 輸出
  .claude/
    settings.json      權限(封鎖裸 python,允許 conda run)
    skills/
      _shared/         共用規範(10 檔;無 SKILL.md,非 skill)
      paper-reading-zh/
      academic-peer-review-zh/
      citation-verification-zh/
      paper-research-logic-review/
      literature-review-organizer/
      method-extraction-social-science/
      paper-search/
      source-document-extraction/
```

## 交接鏈

skill 間的交接已文件化於 `.claude/skills/_shared/handoff.md`:

```
paper-search ─清單─▶ source-document-extraction ─extracted/*.md─▶ 閱讀/分析/審查層 ─▶ literature-review-organizer
```

共用 `extracted/`（抽取全文）與 `output/`（搜尋產物）目錄慣例；每個 skill 自述上下游、收尾建議下一步。**這不是自動 orchestrator**——Claude Code 不會自動連跑 skills，由你推進。

## 已知限制（本版）

- 交接靠慣例與提示，非自動串接（Claude Code 平台限制）。
- `academic-peer-review-zh` 只含學術論文審查路線；計畫書/補助案審查路線不在 Paperdoku 範圍。

## 📄 授權 / License

本 suite 以 **[CC-BY-NC 4.0](LICENSE)**（創用 CC 姓名標示—非商業性 4.0）釋出 © 2026 Cho-Hsun Lu（billy1125）。你可自由分享與修改，但**須標示來源、且不得作商業使用**。內容依「現狀（AS IS）」提供，不負擔任何擔保責任，詳見上方免責聲明。完整授權條文見 [`LICENSE`](LICENSE)；著作權、署名與第三方聲明見 [`NOTICE`](NOTICE)。

本 suite 的設計理念參考了 [**Academic Research Skills**](https://github.com/Imbad0202/academic-research-skills)（作者 Cheng-I Wu，亦採 CC-BY-NC 4.0）的精神與思路；依其授權標示來源：`Based on Academic Research Skills by Cheng-I Wu`。`paper-search` 與 `citation-verification-zh` 透過 `.mcp.json` 呼叫的 **Semantic Scholar MCP server**（外部相依 [`akapet00/semantic-scholar-mcp`](https://github.com/akapet00/semantic-scholar-mcp)，經 `uvx` 執行）不屬於本 repo，其著作權歸原作者；論文資料來源為 [Semantic Scholar](https://www.semanticscholar.org/)。
