---
name: source-document-extraction
description: Extracts text from PDF or Word (.docx) documents and converts it to structured Markdown (.md) by default, for close reading, review, or full-text search. Use whenever a PDF cannot be rendered or read directly, when the full text of a PDF or Word file is needed, or when locating a specific section or page within a document. Handles PDFs, Word files, .docx, text extraction, tables, multi-column layouts, and page or section lookup.
---

# PDF 與 Word 文字擷取

擷取 PDF 或 Word（`.docx`）的文字，**預設轉為結構化 Markdown（`.md`）**，供精讀、審查或全文檢索。適用時機：Read 工具無法渲染 PDF（缺 poppler／pdftoppm）、需要文件全文、或要定位特定章節與頁碼。

輸出檔沿用來源檔名主幹（`input.pdf` → `extracted/input.md`）；擷取後一律讀產出的 `.md`。

## 如何呼叫

- **顯式**：Claude Code 用 `/source-document-extraction input.pdf`；OpenAI Codex 用 `$source-document-extraction report.docx --txt`。
- **自然語言**：描述需求即可（如「這份 PDF 我讀不到，先擷取全文」），由 `description` 自動觸發。

## 環境需求

conda 環境，Python 3.11，跨平台（Windows／macOS〔含 Apple Silicon〕／Linux）。示範用環境名 `research`，任何裝好套件的環境皆可（改用他名時寫成 `conda run -n "${SDE_ENV:-research}" ...`）。

```bash
conda create -n research python=3.11 -y                        # 環境不存在時
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
```

所需套件：`pymupdf`（`import fitz`）、`pdfplumber`、`pymupdf4llm`、`python-docx`、`mammoth`。不可用時提示使用者執行上述安裝，**勿自行改動環境**。

內附腳本為確定性工具，**直接執行、勿改寫指令或增減旗標**；缺少的行為改用既有旗標達成。

## 設定變數與輸出路徑

| 變數 | 用途 | 預設 |
|------|------|------|
| `SDE_OUT_DIR` | 省略 `-o` 時的輸出資料夾（不存在時自動建立） | `extracted` |
| `SDE_HEADINGS` | 逗號分隔的額外章節名，視為 H2（**僅 `--legacy`**） | 空 |

省略 `-o` 時輸出為 `SDE_OUT_DIR/<來源主幹><副檔名>`；副檔名預設 `.md`，`--raw`／`--outline`／`--txt` 為 `.txt`。若使用者的專案有既定的存放位置或檔名，用 `-o` 顯式指定。

## Markdown 後端（PDF）

- **pymupdf4llm（預設）**：依字型推斷標題層級、輸出 Markdown 表格、處理多欄版面，**雙欄論文與含表格的公文、計畫書**結構最好。標題由字型判定，故 `--headings`／`SDE_HEADINGS` 對此後端無效（會提示忽略）。
- **自製後端（`--legacy`）**：跨頁去除重複頁眉頁尾與孤立頁碼、修復斷字、依編號規則套章節 heading、以 `---` 保留頁分隔。章節判定針對**學術論文的英文編號慣例**，可用 `--headings` 擴充；非學術或中文文件的標題辨識通常不如 pymupdf4llm。

選擇原則：先用預設；輸出結構不理想，或需要頁眉頁尾去重、頁分隔、自訂章節名時，才加 `--legacy`。

### 預設清理

PDF 預設後端會清理輸出（`--no-clean` 關閉），採通用啟發式、不對特定文件過度調校：

- 移除反引號、`**` 粗體與 HTML 標籤（如 `<u>`）
- 移除頁分隔、孤立頁碼行，並以頻率偵測移除跨頁重複的頁眉頁尾
- 標題深度收斂到最多 5 層（`#` ~ `#####`），表格與清單（`-`／`1.`）保持單純
- 偵測到**大量**參考文獻／附錄（位於後半且佔比夠大）時**預設忽略**並於 stderr 提示，`--keep-refs` 可保留

Word 路徑（mammoth）同樣預設清理：內嵌 base64 圖片換成佔位標記、移除書籤空錨點與目錄內部連結、還原安全標點的反斜線跳脫，只動標記不動文字。

清理以**安全、不過度**為原則，殘留少量頁眉碎片屬正常；需要更精細的版面改用下述可選的 LLM 步驟。

## 操作步驟

1. **驗證環境**，失敗時提示使用者安裝：
   ```bash
   conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"
   ```
2. **執行腳本**（見「指令」節），輸出 UTF-8 檔。來源檔只讀不改、不搬移。
3. **用 Read 開啟產出的 `.md`** 閱讀內容，回報實際輸出路徑，接續後續處理。
4. **（可選）LLM 版面整理**：程式清理已足夠一般閱讀。使用者想要更漂亮的版面（合併被切斷的段落、對齊表格、修飾標題階層）時**先詢問**再做，因為這會額外耗用 token。原則：**保留所有文字資訊，只重排與修飾格式，不刪改、不摘要**。

### Windows 限制（務必遵守）

- `conda run ... python -c "..."` **不支援含換行的多行腳本**——邏輯寫成 `.py` 檔再執行（內附腳本已處理）。
- 中文直接 `print` 會觸發 **cp950 編碼錯誤**——結果一律寫入 UTF-8 檔案再用 Read 讀取，不要 print 到終端。

## 指令

`SCRIPTS` 代表本技能的 `scripts/` 目錄。

```bash
conda run -n research python SCRIPTS/extract_pdf.py input.pdf      # PDF  -> extracted/input.md
conda run -n research python SCRIPTS/extract_docx.py report.docx   # Word -> extracted/report.md
```

`extract_pdf.py` 旗標：

| 旗標 | 作用 |
|------|------|
| `--margins N` | 裁掉頁首頁尾各 N 點（去頁眉、頁碼干擾） |
| `--keep-refs` | 保留參考文獻／附錄 |
| `--no-clean` | 不做預設清理（保留反引號／粗體／HTML／頁碼） |
| `--legacy` | 改用自製後端 |
| `--pages 5-8,10` | 指定頁碼（1-indexed，支援逗號與區間） |
| `--raw` | 未加工純文字（`.txt`），除錯或需保留原始版面時用 |
| `--outline` | 每頁前 160 字概覽，協助定位章節 |
| `--figures` | 把選定頁 render 成 PNG（獨立模式，不產生文字檔） |
| `--figure-dpi N` | `--figures` 的解析度（預設 150，小字圖可調高） |
| `--headings "a,b"` | 擴充視為章節標題的名稱（僅 `--legacy`） |
| `-o path` | 顯式指定輸出路徑 |

`extract_docx.py` 旗標：`--keep-images`（保留內嵌 base64 圖片）、`--no-clean`（完全不清理）、`--txt`（改用 python-docx 抽段落＋表格純文字）、`-o`。

Word 表格注意：mammoth 會把表格**攤平成段落**——儲存格文字保留，但列欄結構不留（輸出中沒有 Markdown 表格）。需要表格結構時改用 `--txt`，python-docx 會以 `[TABLE n]` 標記包住、每列以 tab 分隔儲存格。

`--figures` 為獨立模式：整頁（而非只抽內嵌圖）render 成 `<輸出目錄>/figures/<主幹>-p<頁碼>.png`，保留向量圖、多子圖與 caption 的脈絡，供以視覺方式判讀純文字擷取讀不到的圖表與公式。務必搭配 `--pages` 限定頁數，否則整份文件每頁都會出圖。

```bash
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --figures --pages 5-6
```

## 內附檔案

- `scripts/extract_pdf.py` —— PDF 擷取入口，涵蓋上表所有旗標。
- `scripts/clean_markdown.py` —— PDF 預設後端的清理器（模組／CLI 雙用）。
- `scripts/to_markdown.py` —— 自製後端：含 `PAGE` 標記的純文字 → Markdown，供 `--legacy` 呼叫，亦可單獨轉換既有 `.txt`。
- `scripts/extract_docx.py` —— Word 擷取入口（預設 mammoth，`--txt` 走 python-docx）。
- `scripts/clean_docx_markdown.py` —— Word 清理器（模組／CLI 雙用）。
- `tests/` —— 兩支自製測試（開發用，跑法見 `README.md`）。
