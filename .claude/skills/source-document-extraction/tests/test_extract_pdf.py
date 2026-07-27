"""驗證 extract_pdf.py 的兩個後端與各模式。

分成兩組：

1. **自足組（一律執行）**：`--figures` 以腳本自製的臨時 PDF 驗證，不需外部檔案。
2. **後端組（需使用者提供 PDF）**：用環境變數 `SDE_TEST_PDF` 指向本機任一份含
   標題與表格的 PDF（學術論文或計畫書皆可），涵蓋——
     - 預設後端 pymupdf4llm：應產生大量標題層級與 Markdown 表格
     - --legacy 自製後端：應保留 PAGE 分隔（轉為 ---）
     - --raw：純文字含 PAGE 標記
     - --outline：首行為 total pages
     - --pages：0-based 頁碼對接（只輸出指定頁）

本技能**不隨附測試用 PDF**（第三方文件不進版控），故未設 `SDE_TEST_PDF` 時只跑
自足組，並印出提示告知如何提供檔案。後端組的斷言刻意寫成 fixture-agnostic，換
任何一份結構正常的 PDF 都應通過。

不依賴 pytest，直接 `conda run -n research python tests/test_extract_pdf.py` 執行；
全數通過印 ALL PASS 並以 0 退出，任一失敗印 FAIL 並以非零退出。

**印到 stdout 的字串一律限 ASCII**：conda run 會用 cp950 轉印子行程 stdout，含中文
或子行程 stderr 原文都可能讓 conda 自己崩潰（見 CLAUDE.md「Windows 限制」）。
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "extract_pdf.py"
# 後端組的測試檔由使用者提供：任一份含標題與表格的 PDF 皆可。
_env_pdf = os.environ.get("SDE_TEST_PDF")
FIXTURE = Path(_env_pdf) if _env_pdf else None


def ascii_safe(s: str) -> str:
    """把字串壓成 ASCII，供 print 到 stdout（cp950 保護，見模組 docstring）。"""
    return s.encode("ascii", "replace").decode("ascii")


def run(out_dir: Path, *args: str) -> Path:
    """執行 extract_pdf.py，回傳輸出檔路徑（以 -o 指定）。"""
    out = out_dir / "out"
    cmd = [sys.executable, str(SCRIPT), str(FIXTURE), "-o", str(out), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    # 失敗訊息也走 ascii_safe：traceback 同樣會經 conda run 的 cp950 轉印
    assert proc.returncode == 0, \
        f"nonzero exit {args}: {ascii_safe(proc.stderr)}"
    assert out.exists() and out.stat().st_size > 0, f"empty output {args}"
    return out


def check_figures(checks: list) -> None:
    """自足驗證 --figures：自製一份雙頁含圖形的 PDF，render 成 PNG 並檢查。"""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pdf = d / "sample.pdf"
        doc = fitz.open()
        for _ in range(2):
            page = doc.new_page()
            page.insert_text((72, 72), "Figure test page")
            page.draw_rect(fitz.Rect(72, 100, 300, 250),
                           color=(0, 0, 1), fill=(0.8, 0.8, 1))
        doc.save(str(pdf))
        doc.close()

        out = d / "out.md"
        cmd = [sys.executable, str(SCRIPT), str(pdf), "-o", str(out),
               "--figures", "--pages", "1"]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8")
        checks.append((f"--figures exit 0 ({ascii_safe(proc.stderr.strip()[:40])})",
                       proc.returncode == 0))
        png = d / "figures" / "sample-p1.png"
        checks.append(("--figures wrote sample-p1.png",
                       png.exists() and png.stat().st_size > 0))
        # --pages 1 只出一張；不應產生 p2
        checks.append(("--figures respects --pages (no p2)",
                       not (d / "figures" / "sample-p2.png").exists()))
        # 未指定 --figures 時不產圖檔（回歸：預設仍是文字 .md）
        out2 = d / "text.md"
        subprocess.run([sys.executable, str(SCRIPT), str(pdf), "-o",
                        str(out2)], capture_output=True, text=True,
                       encoding="utf-8")
        checks.append(("default mode writes .md text", out2.exists()))


def main() -> None:
    # 標籤一律 ASCII：conda run 會用 cp950 轉印子行程 stdout，非 ASCII 會崩潰
    checks: list[tuple[str, bool]] = []

    # --figures 自足驗證（不需外部 fixture，一律執行）
    check_figures(checks)

    if FIXTURE is None or not FIXTURE.exists():
        detail = ("not set" if FIXTURE is None
                  else f"no such file: {ascii_safe(str(FIXTURE))}")
        print(f"NOTE: SDE_TEST_PDF {detail}. Backend tests skipped; only the "
              "self-contained --figures group ran. To run them, point it at "
              "any PDF with headings and tables, e.g.")
        print('      SDE_TEST_PDF="path/to/paper.pdf" conda run -n research '
              "python tests/test_extract_pdf.py")
    else:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)

            # 1) 預設後端 pymupdf4llm（含預設清理）：標題與表格豐富、輸出乾淨
            default_md = run(d / "a").read_text(encoding="utf-8")
            lines = default_md.splitlines()
            n_head = sum(1 for ln in lines if ln.startswith("#"))
            n_table = sum(1 for ln in lines if ln.startswith("|"))
            checks.append((f"pymupdf4llm headings >= 10 (got {n_head})", n_head >= 10))
            checks.append((f"pymupdf4llm table rows >= 5 (got {n_table})", n_table >= 5))
            # 清理：無反引號、無 HTML 標籤、無 ** 粗體、標題深度 <= 5
            checks.append(("clean: no backticks", "`" not in default_md))
            checks.append(("clean: no <u> html tags", "<u>" not in default_md))
            checks.append(("clean: no ** bold", "**" not in default_md))
            deepest = max((len(ln) - len(ln.lstrip("#"))
                           for ln in lines if ln.startswith("#")), default=0)
            checks.append((f"clean: heading depth <= 5 (deepest {deepest})", deepest <= 5))

            # 1b) --no-clean 保留原始標記（回歸）。殘留的標記種類**因文件而異**
            #     （有的出反引號、有的只出 ** 或 HTML 標籤），故不綁單一種類，
            #     只要求清理會移除的三類中至少留下一種——換 fixture 仍成立。
            raw_md = run(d / "a2", "--no-clean").read_text(encoding="utf-8")
            kinds = [name for name, found in (
                ("backticks", "`" in raw_md),
                ("bold", "**" in raw_md),
                ("html", bool(re.search(r"<[a-zA-Z/][^>]*>", raw_md))),
            ) if found]
            checks.append((f"--no-clean keeps raw markup ({','.join(kinds) or 'none'})",
                           bool(kinds)))

            # 2) --legacy：保留頁分隔（to_markdown 把 PAGE 轉為 ---）
            legacy_md = run(d / "b", "--legacy").read_text(encoding="utf-8")
            checks.append(("legacy has page separator ---", "\n---\n" in legacy_md))

            # 3) --raw：純文字含 PAGE 標記
            raw_txt = run(d / "c", "--raw").read_text(encoding="utf-8")
            checks.append(("raw has PAGE markers", "========== PAGE" in raw_txt))

            # 4) --outline：首行 total pages
            outline = run(d / "e", "--outline").read_text(encoding="utf-8")
            checks.append(("outline first line total pages",
                           outline.splitlines()[0].startswith("total pages:")))

            # 5) --pages 1：0-based 對接，只取第 1 頁
            p1 = run(d / "f", "--pages", "1").read_text(encoding="utf-8")
            full = default_md
            checks.append(("pages 1 shorter than full doc", 0 < len(p1) < len(full)))

    ok = True
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed

    print("ALL PASS" if ok else "SOME FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
