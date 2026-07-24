"""將 Markdown（含表格）轉為 Word .docx，使用 Pandoc（透過 pypandoc）。

需在 conda 環境 `research` 下執行，並先安裝（跨平台，含 macOS Apple Silicon）：
    conda run -n research pip install pypandoc
    conda install -n research -c conda-forge pandoc   # 原生二進位，全平台通用
    # 勿用 pypandoc_binary：其內含 pandoc 為 x86_64，Apple Silicon 無法執行

設計理由：本稿為標準學術 Markdown（標題、GFM 表格、引用區塊假設、斜體、編號清單），
Pandoc 能把 pipe table 轉為 Word 原生表格，並可用 --reference-doc 套用期刊樣式範本，
較 python-docx 手刻穩定且程式碼極少。

用法範例：
    # 基本轉換
    conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py Manuscript.md -o Manuscript.docx

    # 套用 Word 樣式範本（字體／行距／表格樣式）
    conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py Manuscript.md -o Manuscript.docx --reference-doc style_reference.docx

    # 產生可編輯的預設樣式範本（之後在 Word 改字體/行距，再用 --reference-doc 套用）
    conda run -n research python .claude/skills/markdown-to-word/scripts/md_to_docx.py --make-reference style_reference.docx

備註：Pandoc 不會自動「合併」視覺上跨列的儲存格（如表 9 的 α/CR/AVE 只寫在首列），
會轉成空白儲存格。若需真正合併，於轉檔後再以 python-docx 後處理。
"""
import argparse
import os
import sys

# 優先鎖定本 conda 環境內的原生 pandoc（<env>/bin/pandoc），避免 pypandoc 先抓到
# PATH 上其他架構（如 x86_64）的 pandoc 而報 "Bad CPU type in executable"。
_env_pandoc = os.path.join(sys.prefix, "bin", "pandoc")
if "PYPANDOC_PANDOC" not in os.environ and os.path.exists(_env_pandoc):
    os.environ["PYPANDOC_PANDOC"] = _env_pandoc

import pypandoc


def make_reference(path: str) -> None:
    """輸出 Pandoc 預設 reference.docx，供使用者在 Word 中調整樣式後重複套用。"""
    data = pypandoc.get_pandoc_path()  # 確保 pandoc 可用（需 PATH 上有 conda-forge 原生 pandoc）
    # 透過 pandoc 內建資料檔輸出預設樣式範本
    import subprocess
    subprocess.run([data, "-o", path, "--print-default-data-file", "reference.docx"],
                   check=True, stdout=open(path, "wb"))
    print(f"done -> {path}（請在 Word 調整樣式後，以 --reference-doc 套用）", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description="Markdown（含表格）→ Word (.docx) via Pandoc")
    ap.add_argument("md", nargs="?", help="輸入 Markdown 路徑，例如 Manuscript.md")
    ap.add_argument("-o", "--out", help="輸出 .docx 路徑")
    ap.add_argument("--reference-doc", help="Word 樣式範本 .docx（套用字體／行距／表格樣式）")
    ap.add_argument("--make-reference", metavar="PATH",
                    help="僅產生可編輯的預設樣式範本到 PATH，不進行轉換")
    args = ap.parse_args()

    if args.make_reference:
        make_reference(args.make_reference)
        return

    if not args.md or not args.out:
        ap.error("轉換模式需要同時提供輸入 Markdown 與 -o 輸出路徑")

    extra_args = []
    if args.reference_doc:
        extra_args.append(f"--reference-doc={args.reference_doc}")

    # 以 gfm（GitHub-Flavored Markdown）解析，確保 pipe tables 轉為 Word 原生表格
    pypandoc.convert_file(
        args.md,
        to="docx",
        format="gfm",
        outputfile=args.out,
        extra_args=extra_args,
    )
    print(f"done -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
