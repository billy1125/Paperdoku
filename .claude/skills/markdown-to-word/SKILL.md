---
name: markdown-to-word
description: 使用 Pandoc（透過 pypandoc）將含表格的 Markdown 稿件或報告（如 reports/ 下的精讀摘要、審查意見書）轉為 Word .docx。當使用者想匯出、產生 Word 版稿件、把 reports/*.md 交稿成 Word、為 docx 套用期刊樣式範本、或建立可編輯的樣式範本時使用。在 research conda 環境執行內附腳本。注意路由：本 skill 只做「Markdown → Word」格式轉換，不產生內容；要產生報告內容請先用對應的閱讀/分析/審查 skill 寫出 reports/*.md，再用本 skill 轉檔。
version: 0.1.0
---

# Markdown 轉 Word

將含表格的 Markdown 稿件或報告（如 `reports/` 下的精讀摘要、審查意見書）轉為 Word `.docx`。以 **Pandoc（透過 `pypandoc`）** 為首選方案：GFM pipe table 會轉為 Word 原生表格，標題、引用區塊、斜體、編號清單皆自動正確處理；並可用 `--reference-doc` 套用期刊樣式範本。

## 何時使用本技能

- 使用者要求匯出、產生 Word（`.docx`）版稿件或報告。
- 使用者想把 `reports/` 內的 markdown 報告（精讀摘要、審查意見書、綜整回顧等）交稿成 Word。
- 使用者想為 Word 產出套用期刊樣式範本。
- 使用者想取得可編輯的樣式範本以定義文件樣式。

## 環境需求

本技能在 conda 環境 **`research`**（Python 3.11）執行（**跨平台：Windows／macOS〔含 Apple Silicon／arm64〕／Linux 通用**）；完整安裝與驗證見專案 `../../../docs/install.md`。為方便單獨使用，以下為本技能自含的最小安裝：

```bash
conda create -n research python=3.11 -y                        # 環境不存在時先建立
conda run -n research pip install pypandoc                      # Python 封裝
conda install -n research -c conda-forge pandoc -y              # 原生 pandoc 二進位，全平台通用
```

> **勿用 `pypandoc_binary`**：其內含的 pandoc 為 x86_64，macOS Apple Silicon 無 Rosetta 時會報 `bad CPU type in executable`。請改用 conda-forge 的原生 `pandoc`（各平台皆有對應 build）。

若 Pandoc 不可用，提示使用者執行上述安裝，勿自行改動環境。

## 操作步驟

1. **先驗證 Pandoc 可用**；失敗時提示使用者安裝上述套件：
   ```bash
   conda run -n research python -c "import pypandoc; print(pypandoc.get_pandoc_path())"
   ```
2. **執行轉換**，產出 `.docx`（見「指令範例」）。輸出檔沿用來源報告的檔名主幹、副檔名改 `.docx`，存回 `reports/`。
3. **（選用）需符合期刊格式時**：先以 `--make-reference` 產生樣式範本，請使用者在 Word 調整字體／行距／表格樣式後，再以 `--reference-doc` 套用。

## 指令範例

```bash
# 基本轉換（把 reports/ 內的報告轉成同主幹的 .docx）
conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py reports/2024-Wang-Forecasting-peer-review.md -o reports/2024-Wang-Forecasting-peer-review.docx

# 套用 Word 樣式範本（字體／行距／表格樣式）
conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py reports/report.md -o reports/report.docx --reference-doc style_reference.docx

# 產生可編輯的預設樣式範本（在 Word 調整後再用 --reference-doc 套用）
conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py --make-reference style_reference.docx
```

## 已知限制

- Pandoc **不會自動合併**視覺上跨列的儲存格（如表 9 的 α/CR/AVE 只寫在首列），會轉成空白儲存格。若需真正合併，於轉檔後再以 python-docx 後處理。
- 標題層級對應：Markdown `#` → Word Heading 1、`##` → Heading 2，依此類推。若需調整（如讓各章 `##` 變 Heading 1），可加 `--shift-heading-level-by`。

## 內附檔案

- `scripts/md_to_docx.py` —— 以 `pypandoc.convert_file(..., format="gfm", to="docx")` 轉換；支援 `--reference-doc` 套樣式、`--make-reference` 產範本。

## 上下游交接

- **本 skill 是終端匯出層**（下游：無；產物直接交付使用者）。
- **上游**：任何寫出 `reports/*.md` 的閱讀/分析/審查/綜整 skill（`paper-reading-zh`、`academic-peer-review-zh`、`paper-research-logic-review`、`literature-review-organizer`、`method-extraction-social-science`、`citation-verification-zh`）。
- **命名**：輸出 `.docx` 沿用來源報告主幹（例：`2024-Wang-Forecasting-peer-review.md` → `2024-Wang-Forecasting-peer-review.docx`），存回 `reports/`；主幹規則見 `../_shared/paper_naming_convention.md`。完整交接鏈見 `../_shared/handoff.md`。
- 本 skill 只轉格式、不改內容，也不套 anti-leakage（不產生新的論文陳述）。
