# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這是什麼

本目錄是一個 **Claude Code Skill**（`source-document-extraction`）的原始碼，不是一般應用程式專案，因此沒有 build／lint 工具鏈。核心是 `SKILL.md`（技能說明與觸發條件）加上 `scripts/` 內四支 Python 腳本（`extract_pdf.py`、`clean_markdown.py`、`to_markdown.py`、`extract_docx.py`），另有 `tests/test_extract_pdf.py`（以實際 PDF 驗證）。

技能用途：這是一個**通用文件擷取技能**，從任意來源擷取 PDF 或 Word（`.docx`）文字，**預設轉為結構化 Markdown（`.md`）**，供 Read 工具讀取。存在理由是部署環境的 Read 工具無法渲染 PDF（缺 poppler／pdftoppm）。技能不綁定特定專案或下游流程。

輸出資料夾（預設 `extracted/`）是**執行期使用者專案的目錄**，不在本 repo 內；本 repo 只含技能本體。腳本以 CLI 參數接受任意輸入／輸出路徑，並未寫死資料夾。

## 執行環境與指令

所有腳本一律在 conda 環境 **`research`**（Python 3.11，跨平台）執行，需先安裝套件：

```bash
conda create -n research python=3.11 -y                        # 環境不存在時
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"   # 驗證環境
conda run -n research python tests/test_extract_pdf.py                   # 以實際 PDF 跑測試
```

常用指令（`SCRIPTS` 代表本技能的 `scripts/` 目錄）。省略 `-o` 時輸出落在 `SDE_OUT_DIR`（預設 `extracted/`）、檔名沿用來源主幹：

```bash
# PDF → Markdown（預設 pymupdf4llm 後端、最常用；輸出 extracted/X.md）
conda run -n research python SCRIPTS/extract_pdf.py X.pdf
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --keep-refs         # 保留參考文獻/附錄
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --no-clean          # 不做預設清理
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --margins 60        # 裁頁首頁尾各 60 點
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --legacy            # 改用自製後端
conda run -n research python SCRIPTS/extract_pdf.py X.pdf -o out/X.md          # 顯式指定輸出
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --raw                # 未加工純文字（.txt）
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --outline            # 每頁前 160 字，定位章節
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --pages 5-8,10       # 指定頁（1-indexed）
conda run -n research python SCRIPTS/extract_pdf.py X.pdf --legacy --headings "scope,definitions"  # 擴充章節名（僅 legacy）

# Word → Markdown（mammoth，保留標題層級）
conda run -n research python SCRIPTS/extract_docx.py report.docx
conda run -n research python SCRIPTS/extract_docx.py report.docx --txt         # python-docx 段落＋表格純文字

# 既有純文字（含 PAGE 標記）單獨轉 Markdown（僅 legacy 後端會產生此中繼檔）
conda run -n research python SCRIPTS/to_markdown.py extracted/X.txt -o extracted/X.md
```

### 設定變數

- `SDE_OUT_DIR` —— 省略 `-o` 時的輸出資料夾（預設 `extracted`，不存在時自動建立）。
- `SDE_HEADINGS` —— 逗號分隔的額外章節名，轉 Markdown 時視為 H2（與 `--headings` 合併，**僅 `--legacy` 後端生效**）。
- `SDE_ENV` —— 僅文件示範用的 conda 環境名慣例（預設 `research`）；腳本不讀取，示範覆寫寫法為 `conda run -n "${SDE_ENV:-research}" ...`。

## 架構重點

PDF → Markdown 有**兩個互斥後端**，預設用 pymupdf4llm：

- **`extract_pdf.py`（預設 pymupdf4llm 後端＋清理）**：用 PyMuPDF（`import fitz`）開檔後，把已開啟的 `doc` 與 0-based 頁碼清單傳給 `pymupdf4llm.to_markdown(doc, pages=..., page_separators=False, margins=..., ignore_code=True)`（`ignore_code=True` 抑制字型誤判的反引號）。`render_pymupdf4llm()` 內含匯入防護（缺套件給安裝提示並非零退出）。之後預設經 `clean_markdown.py` 清理（`--no-clean` 關閉）：去反引號／`**`／HTML、去頁分隔與孤立頁碼、以頻率移除跨頁重複頁眉頁尾（`detect_running()` 由 fitz 每頁前後數行偵測、門檻 `max(3, pages//2)`）、標題深度收斂到 5，並於偵測到大量參考文獻／附錄時預設截斷（`--keep-refs` 保留）。清理採**通用啟發式、不對特定文件過度調校**——殘留少量頁眉碎片屬正常，精修交給可選的 LLM 步驟。
- **`extract_pdf.py --legacy` → `to_markdown.py`（自製後端）**：逐頁 `get_text` 並插入 `========== PAGE N ==========` 標記，交給 `to_markdown()`。`to_markdown.py` 是通用純文字→Markdown 轉換器（可當模組或 CLI）。管線：依 PAGE 標記切頁 → `_find_repeated` 移除跨頁重複 header/footer → `_clean_page` 去孤立頁碼 → `_heading`（羅馬數字、`1.`、`2.1`、`A.`、`COMMON_HEADINGS` 白名單）套 heading → `_join`／`_para_break` 修復斷字與軟斷行 → `•` 轉 `-`。其章節判定偏英文學術編號，中文文件辨識較弱。
- **旁路模式**：`--raw`（純文字含 PAGE 標記）、`--outline`（每頁前 N 字）不走任何 Markdown 後端。
- **`extract_docx.py`** 預設用 mammoth（`convert_to_markdown`）保留標題層級；`--txt` 改用 python-docx 逐段落擷取並以 `[TABLE]` 標記包住表格（與 pymupdf4llm 無關）。

修改擷取邏輯時：pymupdf4llm 後端行為調整靠其參數（`margins`、`table_strategy` 等，見 `render_pymupdf4llm`）。自製後端啟發式集中在 `to_markdown.py`：`COMMON_HEADINGS` 為預設章節集，`to_markdown(..., extra_headings=...)` 可擴充（CLI `--headings` 與 `SDE_HEADINGS` 經 `collect_headings` 合併，`_heading(line, headings)` 吃傳入集合）；重複頁眉頁腳偵測改 `_find_repeated`（其長度／字母門檻避免誤刪表格短數值），段落切分改 `_para_break`。

## Windows 限制（務必遵守）

- `conda run ... python -c "..."` **不支援含換行的多行腳本**——邏輯一律寫成 `.py` 檔再執行。
- 中文直接 `print` 到終端會觸發 **cp950 編碼錯誤**——所有腳本一律將結果**寫入 UTF-8 檔案**再由 Read 讀取；進度訊息只寫 ASCII-safe 字串到 stderr（見各腳本結尾的 `encode("ascii", "replace")`）。新增輸出時延續此慣例。
