# -*- coding: utf-8 -*-
"""把 pymupdf4llm 產出的 Markdown 清理成單純、易讀的版本。

pymupdf4llm 依字型偵測會把大量內文包進反引號、加上 **粗體** 與 <u> 底線，
標題也可能深到 ######。本模組做預設清理：
- 移除 HTML 標籤（如 <u>）、反引號、`**`／`__` 強調標記
- 移除 pymupdf4llm 的頁分隔列與孤立頁碼行（頁碼標示預設不要）
- 標題深度收斂到最多 5 層（# ~ #####）
- 清單維持單純（`-` 與 `1.`），表格（`| ... |`）原樣保留
- 若偵測到「大量」參考文獻／附錄（位於文件後半且佔比夠大），預設從該處
  截斷並回傳提示；可用 keep_refs=True 保留

可當模組（`from clean_markdown import clean_markdown`）或 CLI 使用。
"""
import argparse
import re
import sys
from pathlib import Path

_HTML_TAG = re.compile(r"</?[a-zA-Z][^>]*>")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_USCORE = re.compile(r"__(.+?)__")
_PAGE_SEP = re.compile(r"^\s*-{3,}\s*end of page.*$", re.I)
_NUM_ONLY = re.compile(r"^\s*\d{1,4}\s*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_MAX_HEADING = 5

# 參考文獻／附錄類標題關鍵字（比對時轉小寫；中文不受影響）。刻意不含「附件」，
# 因它在許多表單/計畫書中是欄位名而非附錄。
_REF_KEYWORDS = (
    "參考文獻", "引用文獻", "參考書目",
    "references", "bibliography", "附錄", "appendix",
)


_TRAIL_NUM = re.compile(r"\s*\d{1,4}\s*$")
_WS = re.compile(r"\s+")


def normalize(s: str) -> str:
    """正規化：收斂空白、去除尾端頁碼，供 running header/footer 比對。"""
    return _WS.sub(" ", _TRAIL_NUM.sub("", s.strip())).strip()


def _running_lines(lines: list[str], min_repeat: int) -> set[str]:
    """找出 md 內跨頁重複的整行 running header/footer（去尾頁碼後重複達門檻者）。

    只鎖定夠長、含文字、非標題非表格的行，避免誤刪重複的短表格值。
    """
    from collections import Counter
    counts: Counter[str] = Counter()
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith(("#", "|", "-")):
            continue
        norm = normalize(s)
        if len(norm) >= 6 and any(c.isalnum() for c in norm):
            counts[norm] += 1
    return {n for n, c in counts.items() if c >= min_repeat}


def _boiler_prefix_patterns(boiler: set[str]) -> list[re.Pattern]:
    """把 boilerplate 正規化字串編成「行首頁眉＋可選頁碼」的移除樣式。

    處理 pymupdf4llm 常把頁眉黏到段落開頭的情形（整行或前綴皆可移除）。
    """
    pats = []
    for b in boiler:
        if b:
            pats.append(re.compile(r"^\s*" + re.escape(b) + r"\s*\d{0,4}\s*"))
    return pats


def _strip_inline(s: str) -> str:
    """移除 HTML 標籤、反引號與粗體/底線強調標記。"""
    s = _HTML_TAG.sub("", s)
    s = s.replace("`", "")
    s = _BOLD.sub(r"\1", s)
    s = _USCORE.sub(r"\1", s)
    s = s.replace("**", "")
    return s


def _find_refs_cut(lines: list[str]) -> int | None:
    """回傳應截斷的行索引（該行起到文末視為參考文獻／附錄），無則 None。

    僅當參考文獻／附錄標題位於文件後半、且其後內容佔比夠大時才認定為
    「大量」，避免誤刪表單/計畫書中僅為欄位名的零星提及。
    """
    total = len(lines)
    if total == 0:
        return None
    for i, ln in enumerate(lines):
        m = _HEADING.match(ln)
        if not m:
            continue
        text = m.group(2).strip().lower()
        if not any(k in text for k in _REF_KEYWORDS):
            continue
        if i < total * 0.5:          # 只看後半段
            continue
        tail = total - i
        if tail >= 40 and tail >= 0.20 * total:
            return i
    return None


def clean_markdown(md: str, keep_refs: bool = False,
                   page_count: int | None = None,
                   boilerplate: set[str] | None = None,
                   ) -> tuple[str, str | None]:
    """清理 pymupdf4llm Markdown。回傳 (清理後文字, 提示訊息或 None)。

    page_count 提供時，用於設定整行 running header/footer 的重複門檻
    （max(3, page_count // 2)）；省略則用 3。
    boilerplate 為外部（由 fitz 版面）偵測到的頁眉／頁尾正規化字串，會連同
    整行重複偵測一起，以「行首前綴＋可選頁碼」移除，處理頁眉黏進段落的情形。
    """
    src = [_strip_inline(l).rstrip() for l in md.split("\n")]
    min_repeat = max(3, (page_count // 2)) if page_count else 3
    boiler = set(boilerplate or set()) | _running_lines(src, min_repeat)
    prefixes = _boiler_prefix_patterns(boiler)

    out: list[str] = []
    for line in src:
        if _PAGE_SEP.match(line):                        # 頁分隔列
            continue
        # 移除頁眉（整行或前綴）；多組件頁眉需反覆套用至穩定
        for _ in range(6):
            changed = False
            for pat in prefixes:
                new = pat.sub("", line, count=1)
                if new != line:
                    line, changed = new, True
            if not changed:
                break
        line = line.rstrip()
        h = _HEADING.match(line)
        if h:                                            # 標題深度收斂到 <= _MAX_HEADING
            level = min(len(h.group(1)), _MAX_HEADING)
            text = h.group(2).strip()
            out.append("#" * level + " " + text if text else "")
            continue
        if _NUM_ONLY.match(line) and not line.lstrip().startswith("|"):
            continue                                     # 孤立頁碼行
        out.append(line)

    # 收斂連續空行為單一空行
    collapsed: list[str] = []
    for line in out:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)

    note = None
    if not keep_refs:
        cut = _find_refs_cut(collapsed)
        if cut is not None:
            dropped = len(collapsed) - cut
            collapsed = collapsed[:cut]
            while collapsed and collapsed[-1] == "":
                collapsed.pop()
            note = (f"note: omitted references/appendix tail ({dropped} lines) "
                    f"by default; use --keep-refs to keep it.")

    text = "\n".join(collapsed).strip() + "\n"
    return text, note


def main() -> None:
    ap = argparse.ArgumentParser(description="清理 pymupdf4llm Markdown")
    ap.add_argument("src", help="輸入 .md（pymupdf4llm 產出）")
    ap.add_argument("-o", "--out", required=True, help="輸出 .md 路徑")
    ap.add_argument("--keep-refs", action="store_true",
                    help="保留參考文獻／附錄（預設偵測到大量時忽略）")
    args = ap.parse_args()

    md = Path(args.src).read_text(encoding="utf-8")
    text, note = clean_markdown(md, keep_refs=args.keep_refs)
    Path(args.out).write_text(text, encoding="utf-8")
    if note:
        sys.stderr.write(note + "\n")
    safe = args.out.encode("ascii", "replace").decode("ascii")
    sys.stderr.write(f"done -> {safe} ({len(text)} chars)\n")


if __name__ == "__main__":
    main()
