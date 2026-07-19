"""從 PDF 擷取文字，預設轉為結構化 Markdown，供後續 Read 閱讀。

**預設輸出 Markdown（.md），後端為 pymupdf4llm**：PyMuPDF 官方伴生套件，依字型
大小推斷標題層級、輸出 Markdown 表格、處理多欄版面（雙欄論文尤其受用）。可用
`--margins` 裁掉頁首頁尾帶狀區。

預設會做**清理**（`--no-clean` 關閉）：移除反引號、`**`粗體與 HTML 標籤（如
`<u>`）、頁分隔與孤立頁碼行，標題深度收斂到最多 3 層（`#`／`##`／`###`），
表格與清單保持單純。若偵測到大量參考文獻／附錄（位於後半且佔比夠大），預設
截斷並於 stderr 提示，`--keep-refs` 可保留。

`--legacy` 改用自製後端（to_markdown）：移除跨頁重複 header/footer 與頁碼、修復
斷字、重組段落、依編號規則套章節 heading，並保留 PAGE 分隔；`--headings`／
`SDE_HEADINGS` 僅在此後端生效。需未加工純文字時用 `--raw`。

輸出路徑：省略 `-o` 時，由輸入檔名主幹加副檔名，落在環境變數 `SDE_OUT_DIR`
指定的資料夾（預設 `extracted`）；`-o` 顯式指定時以其為準。

需在裝有 PyMuPDF / pdfplumber / pymupdf4llm 的 conda 環境下執行（預設環境名
`research`，可用任何裝好套件的環境）。因 Windows 終端 cp950 編碼與 `conda run -c`
不支援多行/中文輸出，本腳本一律將結果寫入 UTF-8 檔案，再由其他工具讀取。

用法範例（輸出檔沿用 PDF 檔名主幹）：
    # 擷取整份文件並轉成 Markdown（預設、最常用；輸出 extracted/input.md）
    conda run -n research python scripts/extract_pdf.py input.pdf

    # 裁掉頁首頁尾各 60 點（去除頁眉/頁碼干擾）
    conda run -n research python scripts/extract_pdf.py input.pdf --margins 60

    # 改用自製後端（頁首頁尾去重、PAGE 標記、--headings 擴充）
    conda run -n research python scripts/extract_pdf.py input.pdf --legacy

    # 顯式指定輸出路徑
    conda run -n research python scripts/extract_pdf.py input.pdf -o out/input.md

    # 擷取未加工純文字（除錯或需保留原始版面時）
    conda run -n research python scripts/extract_pdf.py input.pdf --raw

    # 列出每頁前 N 字，協助定位章節
    conda run -n research python scripts/extract_pdf.py input.pdf --outline

    # 把指定頁 render 成 PNG（供 VLM 圖表查核；輸出 extracted/figures/input-p5.png…）
    conda run -n research python scripts/extract_pdf.py input.pdf --figures --pages 5-6

    # 擷取指定頁碼（1-indexed，可用逗號與區間）
    conda run -n research python scripts/extract_pdf.py input.pdf --pages 5-8

    # 擴充要視為章節標題的名稱（僅 --legacy 生效；亦讀環境變數 SDE_HEADINGS）
    conda run -n research python scripts/extract_pdf.py input.pdf --legacy --headings "scope,definitions"
"""
import argparse
import os
import sys

import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean_markdown import clean_markdown, normalize  # noqa: E402
from to_markdown import collect_headings, to_markdown  # noqa: E402


def detect_running(doc, indices: list[int], min_repeat: int,
                   band: int = 3) -> set[str]:
    """用 fitz 版面偵測跨頁重複的頁眉／頁尾。

    頁眉在文字層常為多行（標題＋期別＋頁碼），pymupdf4llm 會併成一行；故取每頁
    前 band 行與後 band 行，各自去尾頁碼後正規化計數，達門檻者視為 running
    header/footer 的組件，回傳其正規化字串集合（供逐一以前綴移除）。"""
    from collections import Counter
    counts: Counter[str] = Counter()
    for i in indices:
        lines = [s.strip() for s in doc[i].get_text().splitlines() if s.strip()]
        if not lines:
            continue
        for s in lines[:band] + lines[-band:]:
            n = normalize(s)
            if len(n) >= 4 and any(ch.isalnum() for ch in n):
                counts[n] += 1
    return {n for n, c in counts.items() if c >= min_repeat}


def default_out(src: str, ext: str) -> str:
    """省略 -o 時的輸出路徑：SDE_OUT_DIR（預設 extracted）/ 輸入主幹 + ext。"""
    out_dir = os.environ.get("SDE_OUT_DIR", "extracted")
    stem = os.path.splitext(os.path.basename(src))[0]
    return os.path.join(out_dir, stem + ext)


def render_figures(doc, indices: list[int], fig_dir: str, stem: str,
                   dpi: int) -> list[str]:
    """把選定頁 render 成 PNG（供 VLM 圖表查核）。

    每頁存為 <fig_dir>/<stem>-p<N>.png（N 為 1-based 頁碼）。回傳輸出路徑清單。
    render 整頁（而非只抽內嵌圖）以保留向量圖、多子圖與 caption 的完整脈絡。"""
    os.makedirs(fig_dir, exist_ok=True)
    paths: list[str] = []
    for i in indices:
        pix = doc[i].get_pixmap(dpi=dpi)
        path = os.path.join(fig_dir, f"{stem}-p{i + 1}.png")
        pix.save(path)
        paths.append(path)
    return paths


def raw_pages(doc, indices: list[int]) -> str:
    """逐頁 get_text，並在每頁前插入 PAGE 標記（供 --raw 與 --legacy 使用）。"""
    parts: list[str] = []
    for i in indices:
        parts.append(f"\n========== PAGE {i + 1} ==========\n")
        parts.append(doc[i].get_text())
    return "".join(parts)


def render_pymupdf4llm(doc, indices: list[int], margins: float) -> str:
    """預設後端：以 pymupdf4llm 直接把（已開啟的）doc 轉為 Markdown。

    doc 直接沿用已開啟的 fitz.Document；indices 為 0-based 頁碼清單。
    缺套件時給明確安裝提示並退出，不自行安裝。
    """
    try:
        import pymupdf4llm
    except ImportError:
        sys.stderr.write(
            "error: default Markdown backend needs pymupdf4llm.\n"
            "install: conda run -n research pip install pymupdf4llm\n"
            "or use the built-in backend instead: add --legacy\n"
        )
        sys.exit(1)
    # ignore_code=True 抑制字型誤判產生的反引號；page_separators=False 不留頁分隔
    return pymupdf4llm.to_markdown(
        doc, pages=indices, page_separators=False, margins=margins,
        ignore_code=True)


def parse_pages(spec: str, page_count: int) -> list[int]:
    """將 '5-8,10,12' 解析為 0-indexed 頁碼清單。"""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a) - 1, int(b)))
        else:
            pages.append(int(part) - 1)
    return [p for p in pages if 0 <= p < page_count]


def main() -> None:
    ap = argparse.ArgumentParser(description="擷取 PDF 文字（預設輸出 Markdown 檔）")
    ap.add_argument("pdf", help="PDF 路徑，例如 input.pdf")
    ap.add_argument("--pages", help="頁碼（1-indexed），如 '5-8,10'；省略則全部")
    ap.add_argument("--legacy", action="store_true",
                    help="改用自製後端（頁首頁尾去重、PAGE 標記、--headings）；預設用 pymupdf4llm")
    ap.add_argument("--margins", type=float, default=0,
                    help="pymupdf4llm 後端：裁掉頁首頁尾各 N 點（去頁眉/頁碼；預設 0）")
    ap.add_argument("--no-clean", action="store_true",
                    help="pymupdf4llm 後端：不做預設清理（保留反引號/粗體/HTML/頁碼）")
    ap.add_argument("--keep-refs", action="store_true",
                    help="pymupdf4llm 後端：保留參考文獻／附錄（預設偵測到大量時忽略）")
    ap.add_argument("--raw", action="store_true",
                    help="輸出未加工純文字（不做 Markdown 後處理）")
    ap.add_argument("--outline", action="store_true",
                    help="僅輸出每頁前 160 字概覽，協助定位章節")
    ap.add_argument("--figures", action="store_true",
                    help="把選定頁 render 成 PNG（供 VLM 圖表查核），輸出到 <輸出目錄>/figures/")
    ap.add_argument("--figure-dpi", type=int, default=150,
                    help="--figures 的解析度 DPI（預設 150；小字圖可調高）")
    ap.add_argument("-n", "--head", type=int, default=160,
                    help="--outline 時每頁取用字數（預設 160）")
    ap.add_argument("--title", help="Markdown 頂層標題（預設用 PDF 檔名主幹）")
    ap.add_argument("--headings",
                    help="額外視為章節標題的名稱（逗號分隔，僅 --legacy 生效）；亦讀環境變數 SDE_HEADINGS")
    ap.add_argument("-o", "--out",
                    help="輸出檔路徑（UTF-8）；省略則用 SDE_OUT_DIR（預設 extracted）")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    indices = (parse_pages(args.pages, doc.page_count)
               if args.pages else list(range(doc.page_count)))
    stem = os.path.splitext(os.path.basename(args.pdf))[0]

    # --figures：獨立模式，render 選定頁為 PNG，不產生文字檔
    if args.figures:
        base = (os.path.dirname(args.out) or ".") if args.out \
            else os.environ.get("SDE_OUT_DIR", "extracted")
        fig_dir = os.path.join(base, "figures")
        paths = render_figures(doc, indices, fig_dir, stem, args.figure_dpi)
        safe = fig_dir.encode("ascii", "replace").decode("ascii")
        print(f"done -> {safe} ({len(paths)} figures)", file=sys.stderr)
        return

    # 純文字（--raw／--outline）用 .txt，Markdown 用 .md
    ext = ".txt" if (args.raw or args.outline) else ".md"
    title = args.title if args.title is not None \
        else os.path.splitext(os.path.basename(args.pdf))[0]

    if args.outline:
        chunks = [f"total pages: {doc.page_count}"]
        for i in indices:
            head = doc[i].get_text().strip().replace("\n", " ")[: args.head]
            chunks.append(f"--- p{i + 1} --- {head}")
        content = "\n".join(chunks)
    elif args.raw:
        content = raw_pages(doc, indices)
    elif args.legacy:
        content = to_markdown(raw_pages(doc, indices), title=title,
                              extra_headings=collect_headings(args.headings))
    else:
        if args.headings:
            sys.stderr.write(
                "note: --headings only applies to --legacy; the default "
                "backend detects headings automatically. ignored.\n")
        md = render_pymupdf4llm(doc, indices, args.margins)
        if args.no_clean:
            content = md
        else:
            min_repeat = max(3, len(indices) // 2)
            boiler = detect_running(doc, indices, min_repeat)
            content, note = clean_markdown(
                md, keep_refs=args.keep_refs, page_count=len(indices),
                boilerplate=boiler)
            if note:
                sys.stderr.write(note + "\n")

    out = args.out if args.out else default_out(args.pdf, ext)
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)

    safe = out.encode("ascii", "replace").decode("ascii")
    print(f"done -> {safe} ({len(indices)} pages)", file=sys.stderr)


if __name__ == "__main__":
    main()
