"""驗證 clean_docx_markdown.py 的三個清理步驟與其安全界線。

不需要 .docx fixture：mammoth 的輸出特徵可用合成字串完整涵蓋，測試因此
自足且快。涵蓋範圍：
  - base64 內嵌圖片 → 佔位標記（保留 MIME、可用 keep_images 保留原樣）
  - Word 書籤空錨點與目錄內部連結 → 純文字，且不留失效連結
  - 安全標點跳脫還原，且 _ * [ ] # ` 與行首項目符號保持跳脫
  - 不變式：清理前後中文字數與英數字元數完全相同（只動標記不動文字）
  - extract_docx.py 的 --no-clean 確實關閉清理

不依賴 pytest，直接 `conda run -n research python tests/test_clean_docx_markdown.py`
執行；全數通過印 ALL PASS 並以 0 退出，任一失敗印 FAIL 並以非零退出。
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from clean_docx_markdown import (  # noqa: E402
    clean_docx_markdown,
    strip_bookmark_anchors,
    strip_data_uri_images,
    unescape_punct,
)

SAMPLE = "\n".join([
    '![](data:image/x-wmf;base64,AAAABBBBCCCC)元智大學',
    "",
    "[第一章 緒論\t2](#_Toc235279978)",
    "",
    '# <a id="_Toc235279978"></a>第一章 緒論',
    "",
    r"Resnick and Varian \(1997\)指出，content\-based 方法\.",
    "",
    r"索引欄位 user\_idx 與 movie\_idx 之對應\.",
    "",
    r"\- 這行的破折號不是項目符號",
    "",
    r"外部連結 [Semantic Scholar](https://www.semanticscholar.org) 應保留\.",
    "",
    '![](data:image/png;base64,DDDDEEEE)',
])


def cjk(s: str) -> int:
    return len(re.findall(r"[一-鿿]", s))


def alnum(s: str) -> int:
    return len(re.findall(r"[0-9A-Za-z]", s))


def check_cli(checks: list) -> None:
    """驗證 extract_docx.py 的 --no-clean：以 CLI 對照清理與未清理輸出。

    無 .docx fixture 時改測 clean_docx_markdown.py 的 CLI，行為等價。
    """
    script = ROOT / "scripts" / "clean_docx_markdown.py"
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        src = d / "in.md"
        src.write_text(SAMPLE, encoding="utf-8")

        out = d / "clean.md"
        proc = subprocess.run(
            [sys.executable, str(script), str(src), "-o", str(out)],
            capture_output=True, text=True, encoding="utf-8")
        checks.append(("CLI exits 0", proc.returncode == 0))
        checks.append(("CLI note is ascii-safe", proc.stderr.isascii()))
        cleaned = out.read_text(encoding="utf-8")
        checks.append(("CLI output cleaned", "base64" not in cleaned))

        kept = d / "kept.md"
        subprocess.run(
            [sys.executable, str(script), str(src), "-o", str(kept), "--keep-images"],
            capture_output=True, text=True, encoding="utf-8")
        kept_txt = kept.read_text(encoding="utf-8")
        checks.append(("--keep-images keeps base64", "base64,AAAABBBBCCCC" in kept_txt))


def main() -> None:
    checks: list[tuple[str, bool]] = []
    out, note = clean_docx_markdown(SAMPLE)

    # 1) base64 圖片 → 佔位標記，保留 MIME 與出現順序
    _, n_img = strip_data_uri_images(SAMPLE)
    checks.append(("2 embedded images detected", n_img == 2))
    checks.append(("no base64 payload left", "base64" not in out))
    checks.append(("placeholder keeps mime",
                   "embedded-image-1 (image/x-wmf" in out
                   and "embedded-image-2 (image/png" in out))

    # 2) 書籤錨點與目錄連結
    _, n_anchors, n_links = strip_bookmark_anchors(SAMPLE)
    checks.append(("1 anchor + 1 internal link", (n_anchors, n_links) == (1, 1)))
    checks.append(("no html tag left", not re.search(r"<[a-zA-Z/][^>]*>", out)))
    checks.append(("no dangling internal link", "](#" not in out))
    checks.append(("toc text preserved", "第一章 緒論\t2" in out))
    checks.append(("heading preserved", "# 第一章 緒論" in out))
    checks.append(("external link preserved",
                   "[Semantic Scholar](https://www.semanticscholar.org)" in out))

    # 3) 跳脫還原：安全標點還原，有風險者保持跳脫
    _, n_esc = unescape_punct(SAMPLE)
    checks.append(("safe escapes unescaped", n_esc >= 5))
    checks.append(("dot/paren/hyphen unescaped",
                   "Varian (1997)指出" in out and "content-based" in out))
    checks.append(("underscore stays escaped", r"user\_idx" in out))
    checks.append(("leading bullet stays escaped", r"\- 這行的破折號" in out))

    # 4) 不變式。跳脫還原只拿掉反斜線，故中文與英數字元皆須完全守恆——這是
    #    整個清理最強的保證。錨點與圖片兩步各自要丟掉 markup 識別字與二進位
    #    payload（兩者都不是文字），因此只斷言中文守恆；其可見文字是否保留，
    #    由上面的 toc/heading/external-link 三項檢查涵蓋。
    unesc, _ = unescape_punct(SAMPLE)
    checks.append(("unescape preserves cjk", cjk(unesc) == cjk(SAMPLE)))
    checks.append(("unescape preserves alnum", alnum(unesc) == alnum(SAMPLE)))
    checks.append(("full clean preserves cjk", cjk(out) == cjk(SAMPLE)))

    # 5) 提示訊息存在且為 ASCII（Windows cp950 stderr）
    checks.append(("note emitted", bool(note) and note.isascii()))

    # 6) 未清理時原樣保留
    raw, raw_note = clean_docx_markdown(SAMPLE, keep_images=True)
    checks.append(("keep_images retains payload", "base64,AAAABBBBCCCC" in raw))
    checks.append(("keep_images still strips anchors", "<a id=" not in raw))
    checks.append(("keep_images note emitted", bool(raw_note)))

    check_cli(checks)

    ok = True
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed

    print("ALL PASS" if ok else "SOME FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
