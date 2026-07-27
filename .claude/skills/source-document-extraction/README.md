# source-document-extraction

從 PDF 或 Word（`.docx`）文件擷取文字，**預設轉為結構化 Markdown（`.md`）**，供 AI 代理或人閱讀、精讀、審查、全文檢索。

這是一個遵循 [Agent Skills 開放規格](https://agentskills.io) 的技能（`SKILL.md` + `scripts/`），可用於 Claude Code、OpenAI Codex 等支援該規格的代理。存在理由：部分環境的檔案讀取工具無法直接渲染 PDF，需先擷取成文字。

## 功能特色

- **PDF → Markdown**：預設用 [`pymupdf4llm`](https://pypi.org/project/pymupdf4llm/)（PyMuPDF 官方伴生套件）——依字型推斷標題層級、輸出 Markdown 表格、處理多欄版面，對雙欄論文與含表格的公文／計畫書結構最佳。
- **預設清理**：移除反引號、`**` 粗體、HTML 標籤、頁分隔與重複頁眉頁尾，標題收斂到最多 5 層（`#` ~ `#####`），清單保持 `-`/`1.`；偵測到大量參考文獻／附錄時預設忽略並提示（`--keep-refs` 保留、`--no-clean` 保留原始標記）。採通用啟發式，不對特定文件過度調校。
- **自製後端（`--legacy`）**：跨頁去除重複頁首頁尾與頁碼、修復斷字、依編號規則套章節 heading、保留 PAGE 分隔；章節名可用 `--headings`／`SDE_HEADINGS` 擴充。
- **Word → Markdown**：預設用 mammoth 保留標題層級，**並預設清理** mammoth 忠實轉出的 Word 內部構造——內嵌 base64 圖片換成佔位標記（單張可達數百 KB，不換掉會讓 `.md` 大到讀不動）、移除書籤空錨點與目錄內部連結、還原安全標點的反斜線跳脫；清理只動標記不動文字（`--keep-images` 保留圖片、`--no-clean` 完全不清理）。`--txt` 改用 python-docx 擷取段落與表格純文字。
- **輔助模式**：`--raw`（未加工純文字）、`--outline`（每頁前 160 字，協助定位章節）、`--pages`（指定頁碼）、`--figures`（把選定頁整頁 render 成 PNG，供以視覺模型查核圖表）。
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
--figures                   把選定頁 render 成 PNG（獨立模式，不產生文字檔）
--figure-dpi 300            --figures 的解析度（預設 150，小字圖可調高）
--headings "scope,defs"     擴充視為章節標題的名稱（僅 --legacy 生效）
-o out/input.md             顯式指定輸出路徑
```

`--figures` 為獨立模式：整頁（而非只抽內嵌圖）render 成 `<輸出目錄>/figures/<主幹>-p<頁碼>.png`，以保留向量圖、多子圖與 caption 的完整脈絡，適合把圖表交給視覺模型查核。搭配 `--pages` 限定頁數，否則整份文件每頁都會出圖。

```bash
conda run -n research python scripts/extract_pdf.py input.pdf --figures --pages 5-6
# → extracted/figures/input-p5.png、input-p6.png
```

## 常用選項（`extract_docx.py`）

```bash
--keep-images               保留內嵌 base64 圖片（預設換成佔位標記）
--no-clean                  完全不清理（保留原始 mammoth 輸出）
--txt                       改用 python-docx 抽段落＋表格純文字（.txt，不清理）
-o out/report.md            顯式指定輸出路徑
```

## 進一步版面整理（可選）

程式清理已足夠一般閱讀。若需要更漂亮的版面（合併被切斷的段落、對齊表格、修飾標題階層），可再交由 LLM 整理——原則是**儘量保留所有文字資訊，只重排、不刪改內容**。這一步建議由使用者決定是否進行，以節省 token 成本。

## 設定變數

| 變數 | 用途 | 預設 |
|------|------|------|
| `SDE_OUT_DIR` | 省略 `-o` 時的輸出資料夾 | `extracted` |
| `SDE_HEADINGS` | 逗號分隔的額外章節名，視為 H2（僅 `--legacy`） | 空 |
| `SDE_ENV` | 文件示範用的 conda 環境名慣例（腳本不讀取） | `research` |
| `SDE_TEST_PDF` | **僅測試用**：`test_extract_pdf.py` 的 PDF 路徑 | 未設（略過該組） |

## 測試

```bash
SDE_TEST_PDF="path/to/paper.pdf" conda run -n research python tests/test_extract_pdf.py
conda run -n research python tests/test_clean_docx_markdown.py
```

不依賴 pytest，全數通過印 `ALL PASS`。`SDE_TEST_PDF` 指向任一份含標題與表格的 PDF（本技能不隨附測試檔），未設時只跑不需檔案的那組。

## 檔案結構

```
source-document-extraction/
├── SKILL.md                     # 技能說明與觸發條件（代理讀取）
├── README.md                    # 本文件
├── CLAUDE.md                    # 給 Claude Code 的開發指引
├── agents/
│   └── openai.yaml              # OpenAI Codex 的顯示用 metadata（名稱/圖示，不影響執行）
├── scripts/
│   ├── extract_pdf.py           # PDF 擷取（預設 pymupdf4llm＋清理，--legacy 走 to_markdown，--figures 出圖）
│   ├── clean_markdown.py        # PDF 預設後端的清理器（去標記/頁眉、收斂標題、截斷參考文獻）
│   ├── to_markdown.py           # 自製後端：純文字（含 PAGE 標記）→ Markdown
│   ├── extract_docx.py          # Word 擷取（mammoth＋清理 / python-docx）
│   └── clean_docx_markdown.py   # Word 清理器（去 base64 圖片/書籤錨點、還原安全跳脫）
└── tests/
    ├── test_extract_pdf.py      # PDF 擷取的兩後端與各模式
    └── test_clean_docx_markdown.py  # Word 清理器
```

## 使用限制

- 純文字擷取器對**數學公式**皆會產生亂碼，這是共通限制，換後端無解。PDF 可用 `--figures` 把該頁 render 成 PNG 改以視覺方式判讀；Word 內的 MathType／WMF 公式物件本身是圖片，會被清理成佔位標記（`--keep-images` 可保留原始 base64）。
- Word 的預設路徑（mammoth）會把**表格攤平成段落**：儲存格文字保留，但列欄結構不留。需要表格結構時改用 `--txt`，python-docx 會以 `[TABLE n]` 標記包住、每列以 tab 分隔儲存格。
- 參考文獻與附錄多半只是佔用篇幅，送給 AI 前可考慮以 `--pages` 截斷。
