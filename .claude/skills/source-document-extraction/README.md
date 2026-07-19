# source-document-extraction

從 PDF 或 Word（`.docx`）文件擷取文字，**預設轉為結構化 Markdown（`.md`）**，供 AI 代理或人閱讀、精讀、審查、全文檢索。

這是一個遵循 [Agent Skills 開放規格](https://agentskills.io) 的技能（`SKILL.md` + `scripts/`），可用於 Claude Code、OpenAI Codex 等支援該規格的代理。存在理由：部分環境的檔案讀取工具無法直接渲染 PDF，需先擷取成文字。

## 功能特色

- **PDF → Markdown**：預設用 [`pymupdf4llm`](https://pypi.org/project/pymupdf4llm/)（PyMuPDF 官方伴生套件）——依字型推斷標題層級、輸出 Markdown 表格、處理多欄版面，對雙欄論文與含表格的公文／計畫書結構最佳。
- **預設清理**：移除反引號、`**` 粗體、HTML 標籤、頁分隔與重複頁眉頁尾，標題收斂到最多 5 層（`#` ~ `#####`），清單保持 `-`/`1.`；偵測到大量參考文獻／附錄時預設忽略並提示（`--keep-refs` 保留、`--no-clean` 保留原始標記）。採通用啟發式，不對特定文件過度調校。
- **自製後端（`--legacy`）**：跨頁去除重複頁首頁尾與頁碼、修復斷字、依編號規則套章節 heading、保留 PAGE 分隔；章節名可用 `--headings`／`SDE_HEADINGS` 擴充。
- **Word → Markdown**：預設用 mammoth 保留標題層級；`--txt` 改用 python-docx 擷取段落與表格純文字。
- **輔助模式**：`--raw`（未加工純文字）、`--outline`（每頁前 160 字，協助定位章節）、`--pages`（指定頁碼）。
- **跨平台**：Windows／macOS（含 Apple Silicon）／Linux；輸出一律 UTF-8 檔案，避開 Windows cp950 終端編碼問題。

## 安裝

在 conda 環境（示範用環境名 `research`，可換）安裝所需套件：

```bash
conda create -n research python=3.11 -y
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"   # 驗證
```

## 快速開始

```bash
# PDF → Markdown（預設 pymupdf4llm；輸出 extracted/input.md）
conda run -n research python scripts/extract_pdf.py input.pdf

# Word → Markdown（輸出 extracted/report.md）
conda run -n research python scripts/extract_docx.py report.docx
```

省略 `-o` 時，輸出落在 `SDE_OUT_DIR`（預設 `extracted/`，自動建立），檔名沿用來源主幹。

## 兩個 PDF Markdown 後端

| | 預設（pymupdf4llm） | `--legacy`（自製） |
|---|---|---|
| 標題層級 | 依字型自動推斷 | 依編號規則（偏英文學術慣例） |
| 表格 | 輸出 Markdown 表格 | 不特別處理 |
| 多欄版面 | 自動處理 | 不處理 |
| 頁首頁尾 | `--margins N` 裁帶狀區 | 跨頁重複偵測並移除 |
| 章節名擴充 | 不適用 | `--headings` / `SDE_HEADINGS` |
| 頁分隔 | `page_separators` | `---` |

選擇原則：預設先用 pymupdf4llm；若輸出結構不理想，或需要頁首頁尾去重、PAGE 分隔、自訂章節名，才加 `--legacy`。

## 常用選項（`extract_pdf.py`）

```bash
--keep-refs                 保留參考文獻／附錄（預設偵測到大量時忽略）
--no-clean                  不做預設清理（保留反引號/粗體/HTML/頁碼）
--margins 60                裁掉頁首頁尾各 60 點（去頁眉/頁碼）
--legacy                    改用自製後端
--raw                       未加工純文字（輸出 .txt）
--outline                   每頁前 160 字概覽，定位章節
--pages 5-8,10              指定頁碼（1-indexed，支援逗號與區間）
--headings "scope,defs"     擴充視為章節標題的名稱（僅 --legacy 生效）
-o out/input.md             顯式指定輸出路徑
```

## 進一步版面整理（可選）

程式清理已足夠一般閱讀。若需要更漂亮的版面（合併被切斷的段落、對齊表格、修飾標題階層），可再交由 LLM 整理——原則是**儘量保留所有文字資訊，只重排、不刪改內容**。這一步建議由使用者決定是否進行，以節省 token 成本。

## 設定變數

| 變數 | 用途 | 預設 |
|------|------|------|
| `SDE_OUT_DIR` | 省略 `-o` 時的輸出資料夾 | `extracted` |
| `SDE_HEADINGS` | 逗號分隔的額外章節名，視為 H2（僅 `--legacy`） | 空 |
| `SDE_ENV` | 文件示範用的 conda 環境名慣例（腳本不讀取） | `research` |

## 測試

以實際 PDF 驗證兩後端與各模式：

```bash
conda run -n research python tests/test_extract_pdf.py
```

全數通過會印 `ALL PASS`。測試 fixture 為 repo 內的一份實際中文計畫書 PDF。

## 檔案結構

```
source-document-extraction/
├── SKILL.md                     # 技能說明與觸發條件（代理讀取）
├── README.md                    # 本文件
├── CLAUDE.md                    # 給 Claude Code 的開發指引
├── scripts/
│   ├── extract_pdf.py           # PDF 擷取（預設 pymupdf4llm＋清理，--legacy 走 to_markdown）
│   ├── clean_markdown.py        # 預設後端的清理器（去標記/頁眉、收斂標題、截斷參考文獻）
│   ├── to_markdown.py           # 自製後端：純文字（含 PAGE 標記）→ Markdown
│   └── extract_docx.py          # Word 擷取（mammoth / python-docx）
└── tests/
    └── test_extract_pdf.py      # 以實際 PDF 驗證
```

## 使用限制

- 純文字擷取器對**數學公式**皆會產生亂碼，這是共通限制，換後端無解。
- 參考文獻與附錄多半只是佔用篇幅，送給 AI 前可考慮以 `--pages` 截斷。
