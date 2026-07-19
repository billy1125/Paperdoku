# -*- coding: utf-8 -*-
"""把帶有 '========== PAGE N ==========' 分頁標記的 PDF 抽取純文字，
轉為結構化、可讀的 Markdown。

設計為通用（不綁定特定論文／期刊）：
- 移除跨頁重複的 running header／footer 與頁首／頁尾孤立頁碼
- 修復 PDF 行尾連字斷字（word-\\n）與軟斷行，重組成段落
- 依常見學術論文編號規則，把章節標題套上 Markdown heading
- bullet（•）統一為 Markdown 的 -

預設章節集（COMMON_HEADINGS）針對學術論文的常見章節與編號慣例。處理其他
類型文件時，可用 `--headings`（逗號分隔）或環境變數 `SDE_HEADINGS` 擴充要
視為 H2 的章節名，例如 `--headings "scope,definitions"`。

可當模組（`from to_markdown import to_markdown`）或 CLI 使用：
    conda run -n research python scripts/to_markdown.py extracted/foo.txt -o extracted/foo.md
"""
import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

PAGE_RE = re.compile(r'^\s*=+\s*PAGE\s+(\d+)\s*=+\s*$')
NUM_LINE_RE = re.compile(r'^\d{1,4}$')

# 預設章節名（小寫比對），命中即視為 H2；可用 extra_headings 擴充
COMMON_HEADINGS = {
    'abstract', 'introduction', 'references', 'conclusion', 'conclusions',
    'acknowledgements', 'acknowledgments', 'discussion', 'related work',
    'background', 'methodology', 'methods', 'results', 'appendix',
    'declaration of competing interest',
    'credit authorship contribution statement',
}


def _split_pages(raw: str) -> list[list[str]]:
    """依 PAGE 標記把全文切成多頁區塊。"""
    pages, cur = [], []
    for ln in raw.split('\n'):
        if PAGE_RE.match(ln):
            pages.append(cur)
            cur = []
        else:
            cur.append(ln.rstrip())
    pages.append(cur)
    return [p for p in pages if any(s.strip() for s in p)]


def _find_repeated(pages: list[list[str]], min_pages: int = 3) -> set[str]:
    """找出跨多頁重複的 running header/footer（期刊名／作者頁腳／版權宣告等）。

    僅鎖定「夠長且含字母」的行，避免誤刪在多個表格重複出現的短數值
    （如相關係數 0.526）。不限長度上限——版權宣告常長達上百字元。
    """
    seen: Counter[str] = Counter()
    for pg in pages:
        for s in {x.strip() for x in pg if x.strip()}:
            seen[s] += 1
    thr = max(min_pages, (len(pages) + 1) // 2)
    return {s for s, c in seen.items()
            if c >= thr and len(s) >= 15 and any(ch.isalpha() for ch in s)}


def _clean_page(lines: list[str], footers: set[str]) -> list[str]:
    out = [s for s in lines if s.strip() and s.strip() not in footers]
    # 去掉頁首／頁尾的孤立頁碼行（不動內文表格中的數字）
    while out and NUM_LINE_RE.match(out[0].strip()):
        out.pop(0)
    while out and NUM_LINE_RE.match(out[-1].strip()):
        out.pop()
    return out


def _heading(line: str, headings: set[str]):
    """判斷是否章節標題，回傳 (level, text) 或 None。"""
    s = line.strip()
    if not s or len(s) > 90:
        return None
    if s.lower().rstrip('.') in headings:
        return (2, s)
    if re.match(r'^[IVXLC]+\.\s+[A-Za-z]', s):              # I. INTRODUCTION
        return (2, s)
    if re.match(r'^\d{1,2}\.\d{1,2}\.?\s+\S', s):            # 2.1 / 2.1. Social response
        return (3, s)
    if re.match(r'^\d{1,2}\.\s+[A-Z]', s) and len(s) < 70:  # 1. Introduction
        return (2, s)
    if re.match(r'^[A-Z]\.\s+[A-Za-z]', s) and len(s) < 70:  # A. Content-based
        return (3, s)
    return None


def _join(buf: list[str]) -> str:
    """把一段的多行智慧接合：行尾連字直接接（修復斷字），否則以空格接。"""
    out = ''
    for i, ln in enumerate(buf):
        ln = ln.strip()
        if i == 0:
            out = ln
        elif out.endswith('-') and not out.endswith('--'):
            out = out[:-1] + ln
        else:
            out = out + ' ' + ln
    return out.strip()


def _para_break(prev: str, cur: str) -> bool:
    """啟發式段落邊界：前一行以句末標點結尾且此行像新句／新項起頭。"""
    if not prev:
        return True
    if prev.rstrip().endswith(('.', '?', ':', '!')):
        c = cur.lstrip()
        if c[:1].isupper() or c[:1].isdigit() or c[:1] == '•':
            return True
    return False


def to_markdown(raw: str, title: str | None = None,
                extra_headings: set[str] | None = None) -> str:
    """主轉換：純文字（含 PAGE 標記）→ Markdown 字串。

    extra_headings：額外要視為 H2 的章節名（會小寫正規化後併入預設集）。
    """
    headings = COMMON_HEADINGS | {
        h.strip().lower() for h in (extra_headings or set()) if h.strip()
    }
    pages = _split_pages(raw)
    footers = _find_repeated(pages)

    cleaned: list[str] = []
    for i, pg in enumerate(pages):
        if i > 0:
            cleaned.append('\x00PAGE')
        cleaned.extend(_clean_page(pg, footers))

    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            para = _join(buf)
            if para:
                out.append(para)
                out.append('')
            buf.clear()

    prev = ''
    for s in cleaned:
        if s == '\x00PAGE':
            # 跨頁斷字：上頁尾以連字結尾時，讓段落續接到下頁，不插分頁線
            if buf and buf[-1].rstrip().endswith('-'):
                continue
            flush()
            if out and out[-1] != '':
                out.append('')
            out.append('---')
            out.append('')
            prev = ''
            continue
        st = s.strip()
        if not st:
            flush()
            continue
        h = _heading(s, headings)
        if h:
            flush()
            out.append('#' * h[0] + ' ' + h[1])
            out.append('')
            prev = h[1]
            continue
        if st.startswith('•'):
            flush()
            out.append('- ' + st[1:].strip())
            prev = st
            continue
        if buf and _para_break(prev, st):
            flush()
        buf.append(st)
        prev = st
    flush()

    md = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'
    if title:
        md = f'# {title}\n\n' + md
    return md


def collect_headings(cli_headings: str | None) -> set[str]:
    """把 CLI --headings 與環境變數 SDE_HEADINGS 合併成集合（逗號分隔）。"""
    result: set[str] = set()
    for src in (os.environ.get('SDE_HEADINGS', ''), cli_headings or ''):
        result |= {h.strip() for h in src.split(',') if h.strip()}
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description='把 PDF 抽取純文字轉為 Markdown')
    ap.add_argument('src', help='輸入純文字檔（含 PAGE 標記）')
    ap.add_argument('-o', '--out', required=True, help='輸出 .md 路徑')
    ap.add_argument('--title', help='文件頂層標題（省略則用輸入檔名主幹）')
    ap.add_argument('--headings',
                    help='額外視為 H2 的章節名（逗號分隔）；亦讀環境變數 SDE_HEADINGS')
    args = ap.parse_args()

    raw = Path(args.src).read_text(encoding='utf-8')
    title = args.title if args.title is not None else Path(args.src).stem
    md = to_markdown(raw, title=title, extra_headings=collect_headings(args.headings))
    Path(args.out).write_text(md, encoding='utf-8')
    # 只寫 ASCII 安全訊息到 stderr，避免 conda run 以 cp950 轉印中文路徑而報錯
    safe = args.out.encode('ascii', 'replace').decode('ascii')
    sys.stderr.write(f'done -> {safe} ({len(md)} chars)\n')


if __name__ == '__main__':
    main()
