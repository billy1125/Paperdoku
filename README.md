# Paperdoku

一套用於**論文閱讀與文獻整理**的 Claude Code skill suite,涵蓋從搜尋、擷取、精讀到多篇綜整的工作流。繁體中文優先,設計哲學參考 human-in-the-loop 的學術研究工具(如 Academic Research Skills):**AI 是副駕駛,幫你處理精讀、比較、查證的粗活,判斷與詮釋仍由你來。**

Suite 版本:0.1.0

## 技能一覽

| Skill | 做什麼 | 模式 |
|---|---|---|
| `paper-reading-zh` | **單篇**論文深入閱讀 | quick-scan / full(預設) / socratic / claim-audit |
| `academic-peer-review-zh` | **單篇**完整同儕審查(下 Accept/Reject 判決;含 RoB、證據等級) | 單一(嚴格/中立/發展) / panel / calibration |
| `citation-verification-zh` | 查核參考文獻**是否真實存在**(揪幻覺引用) | 用 Semantic Scholar MCP |
| `paper-research-logic-review` | **多篇**研究邏輯審查(假設建構與支持狀態) | 3 track |
| `literature-review-organizer` | **多篇**綜整(比較表/缺口/未來方向/回顧;含 PRISMA) | 4 目的 × 4 深度(含 systematic review) |
| `method-extraction-social-science` | **單篇**社科實證方法架構萃取 | 依方法族分支 |
| `paper-search` | 透過 Semantic Scholar 搜尋論文、追引用 | 單一流程 |
| `source-document-extraction` | PDF/Word → 結構化 Markdown;`--figures` 出圖 PNG | 多後端 |

完整的模式對照與路由見 [`MODE_REGISTRY.md`](MODE_REGISTRY.md);工作方式與規則見 [`CLAUDE.md`](CLAUDE.md)。

## 快速開始

安裝為專案技能後(skills 位於 `.claude/skills/`,Claude Code 會自動辨識),直接用自然語言或斜線指令觸發:

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

## 前置需求

- **Claude Code**(最新版)。
- **paper-search 與 citation-verification-zh**:共用 Semantic Scholar MCP;於 `paper-search/README.md` 設定金鑰(無金鑰亦可用,共用匿名速率限制)。MCP 未連線時 `citation-verification-zh` 會誠實告知無法查核,不憑記憶判定。
- **source-document-extraction**:需 conda 環境 `research`(Python 3.11)與擷取套件:
  ```bash
  conda create -n research python=3.11 -y
  conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
  ```
  裸 `python`/`pip` 已於 `.claude/settings.json` 封鎖;一律走 `conda run -n research`。
- 其餘 4 個閱讀/分析 skill 為 prompt 驅動,**不需 Python**。

## 設計要點

- **共用規範集中**:反捏造(anti-leakage)、信心分級、假設支持紀律等收在 `.claude/skills/_shared/`,各 skill 引用而非各自重寫。
- **路由單一真相源**:所有模式與分流集中在 `MODE_REGISTRY.md`。
- **可獨立抽離**:不依賴任何母 repo,整個 `Paperdoku/` 目錄可作為獨立專案搬走使用。

## 目錄結構

```
Paperdoku/
  CLAUDE.md            工作方式 + 路由紀律
  README.md            本檔
  MODE_REGISTRY.md     模式 → skill 路由表
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

共用 `extracted/`(抽取全文)與 `output/`(搜尋產物)目錄慣例;每個 skill 自述上下游、收尾建議下一步。**這不是自動 orchestrator**——Claude Code 不會自動連跑 skills,由你推進。

## 已知限制(本版)

- 交接靠慣例與提示,非自動串接(Claude Code 平台限制)。
- `academic-peer-review-zh` 只含學術論文審查路線;計畫書/補助案審查路線不在 Paperdoku 範圍。
