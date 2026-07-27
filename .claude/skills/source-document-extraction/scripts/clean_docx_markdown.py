# -*- coding: utf-8 -*-
"""把 mammoth 產出的 Word Markdown 清理成單純、易讀的版本。

mammoth 忠實轉出 Word 的內部構造，因此輸出常帶三類對閱讀無用的標記：

1. **內嵌圖片 base64**：Word 內的圖片（含 MathType／WMF 公式物件）會轉成
   `![](data:image/png;base64,...)`，單張就可能數百 KB，讓 .md 膨脹到 Read
   工具讀不動——文字本體往往只佔全檔百分之幾。預設換成佔位標記，保留圖片
   出現的位置與 MIME 型別；`keep_images=True` 保留原樣。
2. **Word 書籤錨點**：目錄與交叉參照會留下 `<a id="_Toc123456"></a>` 這類
   空錨點，以及指向它的 `[標題\t頁碼](#_Toc123456)` 目錄連結。兩者都不帶
   文字內容，移除後改為純文字，不會有失效連結殘留。
3. **防衛性反斜線跳脫**：mammoth 會把 Markdown 有意義的標點全部跳脫，於是
   內文出現大量 `\\.`、`\\(`、`\\)`、`\\-`，中文文獻引註尤其密集。

清理只動標記、不動文字：三個步驟都不會改變任何一個中文字或英數字元。

跳脫還原刻意**只**處理 `. ( ) + - ! { }` 這組還原後不會產生 Markdown 語法的
標點；`_ * [ ] # ` \\` 一律保持跳脫，因為還原它們會讓 `user\\_idx` 之類的識別字
被當成斜體、讓文字被誤判為連結或標題。行首的 `\\-` / `\\+` 亦保持跳脫，避免
變成項目符號。

可當模組（`from clean_docx_markdown import clean_docx_markdown`）或 CLI 使用。
"""
import argparse
import re
import sys
from pathlib import Path

# ![alt](data:image/png;base64,....)　── alt 可有可無
_DATA_URI_IMG = re.compile(r"!\[[^\]]*\]\(data:([^;,)]+)[^)]*\)")
# <a id="..."></a>　── 成對且不含文字的空錨點
_EMPTY_ANCHOR = re.compile(r'<a id="[^"]*"></a>\s*')
# [顯示文字](#錨點)　── 文件內部連結，還原成顯示文字
_INTERNAL_LINK = re.compile(r"\[([^\]]*)\]\(#[^)]*\)")
# 還原後不會產生 Markdown 語法的標點
_SAFE_ESCAPE = re.compile(r"\\([.()+\-!{}])")
# 行首的跳脫項目符號：還原會變成清單
_LEADING_BULLET = re.compile(r"^(\s*\\[-+]\s)")


def strip_data_uri_images(md: str) -> tuple[str, int]:
    """把內嵌 base64 圖片換成保留位置與 MIME 的佔位標記。回傳 (文字, 張數)。"""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"![embedded-image-{count} ({m.group(1)}, binary stripped)]()"

    return _DATA_URI_IMG.sub(repl, md), count


def strip_bookmark_anchors(md: str) -> tuple[str, int, int]:
    """移除空錨點並把內部連結還原成純文字。回傳 (文字, 錨點數, 連結數)。

    先還原連結再移除錨點，順序無關；兩者皆不刪除任何顯示文字。
    """
    md, n_links = _INTERNAL_LINK.subn(r"\1", md)
    md, n_anchors = _EMPTY_ANCHOR.subn("", md)
    return md, n_anchors, n_links


def unescape_punct(md: str) -> tuple[str, int]:
    """還原安全標點的反斜線跳脫（逐行處理以保護行首項目符號）。"""
    total = 0
    out: list[str] = []
    for line in md.split("\n"):
        m = _LEADING_BULLET.match(line)
        head, body = (m.group(1), line[m.end():]) if m else ("", line)
        body, n = _SAFE_ESCAPE.subn(r"\1", body)
        total += n
        out.append(head + body)
    return "\n".join(out), total


def clean_docx_markdown(md: str, keep_images: bool = False,
                        ) -> tuple[str, str | None]:
    """清理 mammoth Markdown。回傳 (清理後文字, 提示訊息或 None)。"""
    stats: list[str] = []

    if not keep_images:
        md, n_img = strip_data_uri_images(md)
        if n_img:
            stats.append(f"{n_img} embedded image(s) -> placeholder")

    md, n_anchors, n_links = strip_bookmark_anchors(md)
    if n_anchors or n_links:
        stats.append(f"{n_anchors} bookmark anchor(s), {n_links} internal link(s)")

    md, n_esc = unescape_punct(md)
    if n_esc:
        stats.append(f"{n_esc} backslash escape(s)")

    text = md.strip() + "\n"
    note = ("note: cleaned " + "; ".join(stats) +
            "; use --no-clean to keep raw mammoth output.") if stats else None
    return text, note


def main() -> None:
    ap = argparse.ArgumentParser(description="清理 mammoth 產出的 Word Markdown")
    ap.add_argument("src", help="輸入 .md（mammoth 產出）")
    ap.add_argument("-o", "--out", required=True, help="輸出 .md 路徑")
    ap.add_argument("--keep-images", action="store_true",
                    help="保留內嵌 base64 圖片（預設換成佔位標記）")
    args = ap.parse_args()

    md = Path(args.src).read_text(encoding="utf-8")
    text, note = clean_docx_markdown(md, keep_images=args.keep_images)
    Path(args.out).write_text(text, encoding="utf-8")
    if note:
        sys.stderr.write(note + "\n")
    safe = args.out.encode("ascii", "replace").decode("ascii")
    sys.stderr.write(f"done -> {safe} ({len(text)} chars)\n")


if __name__ == "__main__":
    main()
