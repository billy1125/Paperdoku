# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這是什麼

本目錄是一個 **Claude Code Skill**（`source-document-extraction`）的原始碼，不是應用程式專案，沒有 build／lint 工具鏈。核心是 `SKILL.md`（代理讀取的技能說明與觸發條件）加上 `scripts/` 五支 Python 腳本與 `tests/` 兩支自製測試；`agents/openai.yaml` 只是 OpenAI Codex 的顯示用 metadata，不影響執行。

技能用途是**通用文件擷取**：把任意來源的 PDF 或 Word（`.docx`）轉為結構化 Markdown 供 Read 讀取，存在理由是部署環境的 Read 無法渲染 PDF（缺 poppler／pdftoppm）。輸出資料夾（預設 `extracted/`）屬於執行期的使用者專案，不在本技能內；腳本以 CLI 參數接受任意輸入／輸出路徑，未寫死資料夾。

**可攜性紀律（最重要）**：本技能刻意**不綁定任何 repo**——`SKILL.md` 不得寫入具名專案路徑、固定目錄結構或其他技能的名稱（詳見下方「文件同步」節）。被某個專案內嵌（vendored）使用時，「上游來源在哪、產出要落到哪個檔、由哪支技能接手」這類接線一律寫在**該專案自己的文件**裡，不寫回這裡；例如在 Paperforger 專案中，接線寫在其根目錄 `CLAUDE.md` 第 4 節「接線註記」。

本目錄可能是**獨立 checkout**，也可能是**被更大的 repo 內嵌**的一個子目錄——動 git 前先確認實際所在的 repo（本目錄本身未必有 `.git`），不要假設提交歷史屬於本技能。

## 執行環境與測試

所有腳本一律在 conda 環境 **`research`**（Python 3.11，跨平台）執行：

```bash
conda create -n research python=3.11 -y                        # 環境不存在時
conda run -n research pip install pymupdf pdfplumber pymupdf4llm python-docx mammoth
conda run -n research python -c "import fitz, pdfplumber, pymupdf4llm"   # 驗證環境

# 測試（不依賴 pytest，全通過印 ALL PASS）。SDE_TEST_PDF 指向任一份含標題與表格的 PDF
SDE_TEST_PDF="path/to/paper.pdf" conda run -n research python tests/test_extract_pdf.py
conda run -n research python tests/test_clean_docx_markdown.py
```

擷取指令與全部旗標見 `SKILL.md`「指令」節，本檔不重列。`SDE_ENV` 只是文件示範的環境名慣例（預設 `research`），腳本不讀取；`SDE_OUT_DIR`／`SDE_HEADINGS` 見 `SKILL.md`。

## 架構重點

PDF → Markdown 有**兩個互斥後端**，預設用 pymupdf4llm：

- **預設（pymupdf4llm ＋清理）**：`extract_pdf.py` 以 PyMuPDF（`import fitz`）開檔，把已開啟的 `doc` 與 0-based 頁碼清單交給 `pymupdf4llm.to_markdown(doc, pages=..., page_separators=False, margins=..., ignore_code=True)`（`ignore_code=True` 抑制字型誤判的反引號），`render_pymupdf4llm()` 內含缺套件的匯入防護。之後預設經 `clean_markdown.py`：去反引號／`**`／HTML、去頁分隔與孤立頁碼、移除跨頁重複頁眉頁尾、標題深度收斂到 5，並在偵測到大量參考文獻／附錄時截斷。清理採**通用啟發式、不對特定文件過度調校**——殘留少量頁眉碎片屬正常，精修交給可選的 LLM 步驟。
- **`--legacy` → `to_markdown.py`（自製後端）**：逐頁 `get_text` 並插入 `========== PAGE N ==========` 標記後交給 `to_markdown()`。管線為：依 PAGE 切頁 → `_find_repeated` 移除跨頁重複 header/footer → `_clean_page` 去孤立頁碼 → `_heading`（羅馬數字、`1.`、`2.1`、`A.`、`COMMON_HEADINGS` 白名單）套 heading → `_join`／`_para_break` 修復斷字與軟斷行 → `•` 轉 `-`。章節判定偏英文學術編號，中文文件辨識較弱。
- **旁路與獨立模式**：`--raw`、`--outline` 不走任何 Markdown 後端。`--figures` 是**獨立模式**——`render_figures()` 以 `doc[i].get_pixmap(dpi=...)` 把整頁 render 成 `<輸出目錄>/figures/<主幹>-p<頁碼>.png`（1-based），印出張數後**直接 return，不產生文字檔**。render 整頁而非只抽內嵌圖，是為了保留向量圖、多子圖與 caption 的脈絡。
- **Word 路徑**：`extract_docx.py` 預設用 mammoth（`convert_to_markdown`）保留標題層級，轉出後再經 `clean_docx_markdown.py`；`--txt` 改用 python-docx 逐段落擷取並以 `[TABLE]` 標記包住表格，不經 mammoth，故不清理。**mammoth 不輸出表格**——儲存格文字會攤平成段落（實測 1.3 MB 計畫書：python-docx 找到 3 個表格，mammoth 輸出零個 `|` 列與零個 `<table>`，但儲存格文字仍在），需要列欄結構只能走 `--txt`。

**頁眉去除是兩路偵測合併**：`extract_pdf.detect_running()` 走 fitz 版面（每頁前後各 3 行、門檻 `max(3, pages//2)`）、`clean_markdown._running_lines()` 走 pymupdf4llm 產出的整行重複，兩者聯集後由 `_boiler_prefix_patterns()` 編成「行首＋可選頁碼」樣式，逐行反覆套用最多 6 次——因為 pymupdf4llm 常把多組件頁眉黏成一行接在段落開頭，單次比對移不乾淨。

**`clean_docx_markdown.py` 的核心不變式是「只動標記、不動文字」**。它處理 mammoth 忠實轉出 Word 內部構造的三類標記：內嵌 base64 圖片（含 MathType／WMF 公式物件，單張可達數百 KB，會讓 `.md` 大到 Read 讀不動）換成保留 MIME 的佔位標記、書籤空錨點（`<a id="_Toc…">`）與指向它的目錄內部連結還原成純文字、防衛性反斜線跳脫還原。跳脫還原刻意只處理 `. ( ) + - ! { }` 這組還原後不產生 Markdown 語法的標點；`_ * [ ] # \` \\` 與行首的 `\-`／`\+` 一律保持跳脫，否則 `user\_idx` 會被當斜體、文字會被誤判成連結或清單。

修改擷取邏輯時：pymupdf4llm 的行為靠其參數調整（`margins`、`table_strategy` 等，見 `render_pymupdf4llm`）。自製後端的啟發式集中在 `to_markdown.py`——章節集是 `COMMON_HEADINGS`（`--headings` 與 `SDE_HEADINGS` 經 `collect_headings` 合併後由 `to_markdown(..., extra_headings=...)` 傳入）、重複頁眉頁腳改 `_find_repeated`（其長度／字母門檻避免誤刪表格短數值）、段落切分改 `_para_break`。Word 清理規則集中在 `clean_docx_markdown.py` 頂端的五個 regex；**放寬 `_SAFE_ESCAPE` 的字元集前務必確認還原後不會產生 Markdown 語法**，並讓 `tests/test_clean_docx_markdown.py` 的中文／英數字元守恆斷言維持通過。

## 跨檔慣例

- **同目錄 import**：`extract_pdf.py`／`extract_docx.py` 先 `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` 再 `from clean_markdown import ...`，讓腳本從任意工作目錄執行都載得到同目錄模組（`tests/` 同理 insert `scripts/`）。新增腳本沿用，不要改成套件相對匯入——`scripts/` 沒有 `__init__.py`，也不打算加。
- **清理器一律「模組＋CLI」雙用**：`clean_markdown.py`、`clean_docx_markdown.py`、`to_markdown.py` 的核心函式吃字串回傳字串（兩支 `clean_*` 另回傳一則 ASCII 提示或 `None`），`main()` 只做讀寫檔與寫 stderr。新增清理步驟時把邏輯留在可單獨匯入測試的函式裡。
- **`--title` 與 `--headings` 都只對 `--legacy` 生效**：`title` 只傳給 `to_markdown()`，pymupdf4llm 路徑完全不用。差別在誤用 `--headings` 會印提示，`--title` 則靜默忽略。
- **測試涵蓋缺口**：`extract_docx.py` 本身沒有自動測試——Word 路徑只覆蓋到 `clean_docx_markdown.py`（含其 CLI）。動到它時需自備實際 `.docx` 手動確認：檢查中文字數在清理前後守恆、無 `base64`／`<a id=`／`](#` 殘留、標題數合理，並與 `--txt` 對照表格是否遺漏。

## 文件同步（改旗標時務必檢查）

同一組旗標、預設值與行為描述同時存在於 `SKILL.md`、`README.md`、本檔與各腳本的 module docstring，任一處改動都要一起更新，否則代理會照過時的說明操作。最容易漏掉的是 docstring——它不影響執行、測試也抓不到，只能靠改動時順手核對。

寫 `SKILL.md` 時另有兩條原則：**不綁定任何特定專案或其他技能**（只講通用行為：來源檔不動、`-o` 覆寫落檔位置、回報路徑後接 Read，不寫入具名技能、固定目錄結構或檔名慣例）；**同一資訊只寫一次**（輸出路徑規則、後端選擇、旗標語意分別落在「設定變數與輸出路徑」、「Markdown 後端」、「指令」三節，「內附檔案」節只列各檔職責、不重列旗標）。

## Windows 限制（務必遵守）

- `conda run ... python -c "..."` **不支援含換行的多行腳本**——邏輯一律寫成 `.py` 檔再執行。
- 中文直接 `print` 到終端會觸發 **cp950 編碼錯誤**——所有腳本一律將結果**寫入 UTF-8 檔案**再由 Read 讀取；進度訊息只寫 ASCII-safe 字串到 stderr（見各腳本結尾的 `encode("ascii", "replace")`）。
- **測試印到 stdout 的內容同樣限 ASCII**：`conda run` 會以 cp950 轉印子行程 stdout，含中文的檢查標籤、或直接轉印子行程 stderr 原文（traceback、含中文路徑的訊息）都可能讓 `conda run` 自己崩潰。兩支測試因此全用 ASCII 標籤並以 `ascii_safe()` 包裝外部字串，新增檢查項時沿用。
