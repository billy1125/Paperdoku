---
name: source-document-extraction
description: Extracts text from PDF or Word (.docx) documents and converts it to structured Markdown (.md) by default, for close reading, review, or full-text search. Use whenever a PDF cannot be rendered or read directly, when the full text of a PDF or Word file is needed, or when locating a specific section or page within a document. Handles PDFs, Word files, .docx, text extraction, tables, multi-column layouts, and page or section lookup.
version: 0.1.0
---

# PDF 與 Word 文字擷取

擷取 PDF 或 Word（`.docx`）文件的文字，**預設轉為結構化 Markdown（`.md`）**。當本機 Read 工具無法渲染 PDF（缺 poppler／pdftoppm）時，改用本技能把來源文件擷取成可 Read 的 Markdown。

輸出檔沿用來源檔名主幹（`input.pdf` → `extracted/input.md`），供接續的精讀、審查或全文檢索閱讀——後續一律讀擷取產出的 `.md` 檔。

PDF 預設以 **pymupdf4llm** 後端轉 Markdown（依字型推斷標題層級、輸出表格、處理多欄版面）；`--legacy` 可切回自製後端（頁首頁尾去重、章節 heading、PAGE 分隔）。需要未加工純文字（除錯或保留原始版面）時，PDF 用 `--raw`、Word 用 `--txt`。詳見「Markdown 後端」節。

## 何時使用本技能

- 要讀取 PDF 或 Word 全文，但 Read 工具無法渲染，需先擷取成文字。
- 需在文件中定位特定章節、小節或頁碼範圍。

## 如何呼叫本技能

安裝為技能後，有兩種呼叫方式（顯式呼叫語法依工具而異）：

- **顯式呼叫**：在 Claude Code 用斜線指令 `/source-document-extraction`；在 OpenAI Codex 用 `$source-document-extraction`。可在後面帶上檔案路徑，例如：
  ```text
  /source-document-extraction input.pdf
  $source-document-extraction report.docx --txt
  ```
- **自然語言（由 description 自動觸發）**：描述需求即可，例如「把 input.pdf 轉成 Markdown 讓我閱讀」「這份 PDF 我讀不到，先擷取全文」，代理會依 `description` 判斷並套用本技能。

## 環境需求

本技能在 conda 環境執行（Python 3.11，**跨平台：Windows／macOS〔含 Apple Silicon〕／Linux 通用**）。文件示範用的預設環境名為 **`research`**，但可用任何裝好下列套件的環境。自含的最小安裝：

```bash
conda create -n research python=3.11 -y                        # 環境不存在時先建立
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
```

所需套件：`pymupdf`（`import fitz`）、`pdfplumber`、`pymupdf4llm`（預設 PDF 後端）、`python-docx`、`mammoth`。若不可用，提示使用者執行上述安裝，勿自行改動環境。

若採用其他環境名，可用環境變數示範覆寫：`conda run -n "${SDE_ENV:-research}" ...`。

內附腳本為確定性工具，請**直接執行、勿改寫指令或增減旗標**（缺少的行為改用既有旗標達成，見下）。

## 設定變數

| 變數 | 用途 | 預設 |
|------|------|------|
| `SDE_OUT_DIR` | 省略 `-o` 時的輸出資料夾 | `extracted` |
| `SDE_HEADINGS` | 逗號分隔的額外章節名，轉 Markdown 時視為 H2 標題（**僅 `--legacy` 後端生效**） | 空 |

輸出路徑：省略 `-o` 時，由輸入檔名主幹加副檔名，落在 `SDE_OUT_DIR` 指定的資料夾（預設 `extracted`，不存在時自動建立）；需要別的位置時用 `-o` 顯式指定。

## Markdown 後端（PDF）

PDF 轉 Markdown 有兩個後端，預設用前者：

- **pymupdf4llm（預設）**：PyMuPDF 官方伴生套件，依字型大小自動推斷標題層級、輸出 Markdown 表格、處理多欄版面。**雙欄論文、含表格的公文與計畫書**用這個結構最好。可用 `--margins N` 裁掉頁首頁尾各 N 點（去除頁眉、頁碼干擾）。標題由字型自動判定，故 `--headings`／`SDE_HEADINGS` 對此後端無效（會提示忽略）。
- **自製後端（`--legacy`）**：跨頁去除重複 running header/footer 與孤立頁碼、修復斷字、依編號規則套章節 heading，並以 `---` 保留頁分隔。其章節判定針對**學術論文的英文編號慣例**，可用 `--headings`／`SDE_HEADINGS` 擴充；遇非學術或中文文件時，標題辨識通常不如 pymupdf4llm。

選擇原則：預設先用 pymupdf4llm；若該文件輸出結構不理想，或需要頁首頁尾去重、PAGE 分隔、自訂章節名，才加 `--legacy`。

### 預設清理（pymupdf4llm 後端）

pymupdf4llm 後端**預設會清理**輸出（`--no-clean` 關閉），採通用啟發式、不對特定文件過度調校：

- 移除反引號、`**` 粗體與 HTML 標籤（如 `<u>`）
- 移除頁分隔、孤立頁碼行，並以頻率偵測移除跨頁重複的頁眉／頁尾
- 標題深度收斂到最多 5 層（`#` ~ `#####`）；表格與清單（`-`／`1.`）保持單純
- 偵測到**大量**參考文獻／附錄（位於後半且佔比夠大）時，**預設忽略**並於 stderr 提示，`--keep-refs` 可保留

清理以**安全、不過度**為原則：殘留的少量頁眉碎片或版面瑕疵屬正常，不再逐一硬修——需要更精細的版面，改由下述可選的 LLM 步驟處理。

## 操作步驟

1. **先驗證環境**；失敗時提示使用者安裝上述套件：
   ```bash
   conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"
   ```
2. **執行內附腳本**，將結果輸出為 UTF-8 `.md` 檔（見「指令範例」）。
3. **用 Read 工具開啟產出的 `.md` 檔**閱讀內容，接續後續處理。
4. **（可選）詢問使用者是否要由 LLM 進一步整理版面**。程式清理已足夠一般閱讀；若使用者想要更漂亮的版面（合併被切斷的段落、對齊表格、修飾標題階層等），**先詢問**再做，因為這會額外耗用 token。原則：**儘可能保留所有文字資訊，只做重排與格式修飾，不刪改、不摘要內容**。使用者不需要時就維持程式輸出，以節省成本。

### Windows 限制（務必遵守）

- `conda run ... python -c "..."` **不支援含換行的多行腳本**——必須把程式寫成 `.py` 檔再執行（內附腳本已處理）。
- 中文直接 `print` 會觸發 **cp950 編碼錯誤**——腳本一律**將結果寫入 UTF-8 檔案**，再用 Read 讀取，不要 print 到終端。

## 指令範例

> 以下用中性檔名 `input.pdf` / `report.docx` 示範。省略 `-o` 時輸出落在 `extracted/`（可由 `SDE_OUT_DIR` 覆寫），檔名沿用來源主幹，**預設副檔名為 `.md`**。`SCRIPTS` 代表本技能的 `scripts/` 目錄路徑。

```bash
# PDF：擷取整份文件並轉成 Markdown（預設 pymupdf4llm 後端、最常用；輸出 extracted/input.md）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf

# PDF：裁掉頁首頁尾各 60 點（去頁眉/頁碼干擾）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --margins 60

# PDF：改用自製後端（頁首頁尾去重、PAGE 分隔、可 --headings 擴充章節名）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --legacy

# PDF：顯式指定輸出路徑
conda run -n research python SCRIPTS/extract_pdf.py input.pdf -o out/input.md

# PDF：擷取未加工純文字（除錯或需保留原始版面時；輸出 .txt）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --raw

# PDF：列出每頁前 160 字概覽，協助定位章節（1-indexed 頁碼）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --outline

# PDF：擷取指定頁全文（支援逗號與區間，如 5-8,10）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --pages 5-8

# PDF：保留參考文獻／附錄（預設偵測到大量時忽略）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --keep-refs

# PDF：不做預設清理（保留反引號/粗體/HTML/頁碼等原始標記）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --no-clean

# PDF：擴充要視為章節標題的名稱（僅 --legacy 生效；亦讀環境變數 SDE_HEADINGS）
conda run -n research python SCRIPTS/extract_pdf.py input.pdf --legacy --headings "scope,definitions"

# 既有純文字（含 PAGE 標記）單獨轉 Markdown（僅自製後端會產生此中繼檔）
conda run -n research python SCRIPTS/to_markdown.py extracted/input.txt -o extracted/input.md

# Word：mammoth 轉 Markdown（預設、保留標題層級；輸出 extracted/report.md）
conda run -n research python SCRIPTS/extract_docx.py report.docx

# Word：python-docx 擷取段落＋表格純文字（除錯或需保留表格原貌時）
conda run -n research python SCRIPTS/extract_docx.py report.docx --txt
```

## 內附檔案

- `scripts/extract_pdf.py` —— PyMuPDF 開檔；**預設以 pymupdf4llm 轉 Markdown 並清理**，`--no-clean` 關閉清理、`--keep-refs` 保留參考文獻／附錄、`--legacy` 改走自製 `to_markdown` 後端、`--margins` 裁頁首頁尾、`--raw` 輸出純文字、`--outline` 概覽定位章節、`--pages` 抽特定頁、`--figures`（＋`--figure-dpi`，預設 150）把選定頁 render 成 PNG 到 `<輸出目錄>/figures/`（供 VLM 圖表查核，見 `../_shared/figure_fidelity.md`）、`--headings`（僅 `--legacy`）擴充章節名；省略 `-o` 時依 `SDE_OUT_DIR` 落檔，輸出 UTF-8 檔。
- `scripts/clean_markdown.py` —— 預設後端的清理器：移除反引號／`**`／HTML 標籤、頁分隔與孤立頁碼、頻率偵測的跨頁頁眉頁尾，標題深度收斂到 5，並可依體積門檻截斷大量參考文獻／附錄。可當模組或 CLI 使用。
- `scripts/to_markdown.py` —— 自製後端（`--legacy`）：把含 `PAGE` 標記的擷取純文字轉為結構化 Markdown（移除 header/footer 與頁碼、修復斷字、重組段落、套章節 heading）。預設章節集針對學術論文編號慣例，可用 `--headings`／`SDE_HEADINGS` 擴充。供 `extract_pdf.py --legacy` 呼叫，亦可當 CLI 單獨轉換既有 `.txt`。
- `scripts/extract_docx.py` —— **預設以 mammoth 轉 Markdown**（保留標題層級）；`--txt` 改用 python-docx 擷取段落／表格純文字；省略 `-o` 時依 `SDE_OUT_DIR` 落檔。
- `tests/test_extract_pdf.py` —— 以實際 PDF 驗證兩後端、清理與各模式（標題／表格數、清理後無反引號／HTML／粗體且標題 ≤5、`--no-clean` 保留原始標記、`--legacy` 頁分隔、`--raw`／`--outline`／`--pages`）；`conda run -n research python tests/test_extract_pdf.py`，全通過印 `ALL PASS`。

## 上下游交接

- **本 skill 是全 suite 的 PDF 入口**。上游：`paper-search` 的候選（下載 PDF 後）或使用者提供的 PDF/Word。
- **下游**：產出 `extracted/<主幹>.md`，供所有閱讀/分析/審查 skill（`paper-reading-zh`、`method-extraction-social-science`、`paper-research-logic-review`、`academic-peer-review-zh`、`citation-verification-zh`、`literature-review-organizer`）直接 Read。
- 抽完可建議下一步（如「已抽成 extracted/X.md，要精讀用 paper-reading-zh」）。鏈見 `../_shared/handoff.md`。
