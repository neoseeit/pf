#!/usr/bin/env python3
"""
Check that a built page carries exactly the same text and formatting as its
Notion export.

Both files are reduced to the same list of blocks: every paragraph becomes a
list of runs (text, bold, italic, gray), with boxes, blank lines and headings
kept in order. The two lists must match exactly, character for character.

Also writes a plain-text copy of the source next to it (SOURCE.txt) that is
easy to read through: **bold**, _italic_, ⟨gray⟩.

Usage:
  python3 tools/check_text.py SOURCE.notion.html BUILT.html [EXPECTED_TITLE]

  EXPECTED_TITLE: when the site uses a different title than Notion, check against that instead.
"""
import pathlib
import sys
import urllib.parse

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


def classes(el):
    return el.get("class") or []


CHECK_FILES = False
OUT_DIR = pathlib.Path(".")


def image_name(src):
    """Images are renamed lowercase-with-dashes when copied; compare on that name."""
    return pathlib.Path(urllib.parse.unquote(src)).name.lower().replace(" ", "-")


# ---------- how each side marks gray / blank lines ----------

def src_gray(el):
    c = classes(el)
    return "highlight-gray" in c or "block-color-gray" in c


def out_gray(el):
    return "d" in classes(el)


def src_blank(p):
    return p.get_text().strip() == "" and not p.find("br")


def out_blank(p):
    return "gap" in classes(p)


# ---------- runs ----------

def runs(p, gray):
    out = []

    def walk(n, b, i, g):
        if isinstance(n, Comment):
            return
        if isinstance(n, NavigableString):
            out.append([str(n), b, i, g])
            return
        if n.name == "br":
            out.append(["\n", False, False, False])  # a line break has no visible style
            return
        nb = b or n.name in ("strong", "b")
        ni = i or n.name in ("em", "i")
        ng = g or gray(n)
        for c in n.children:
            walk(c, nb, ni, ng)

    walk(p, False, False, gray(p))
    merged = []
    for r in out:
        if r[0] == "":
            continue
        if merged and merged[-1][1:] == r[1:]:
            merged[-1][0] += r[0]
        else:
            merged.append(r)
    return [tuple(r) for r in merged]


def blocks(container, gray, blank, heading_shift):
    """Flatten a page into blocks. Unknown elements that carry text stop the check,
    so nothing can be skipped silently."""
    seq = []

    def walk(el):
        for k in el.children:
            if isinstance(k, NavigableString) and not isinstance(k, Comment):
                if str(k).strip():
                    raise SystemExit(f"loose text outside a paragraph: {str(k)[:60]!r}")
                continue
            if not isinstance(k, Tag):
                continue
            c = classes(k)
            if k.name == "p":
                seq.append(("blank",) if blank(k) else ("p", runs(k, gray)))
            elif k.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                seq.append((f"heading {int(k.name[1]) - heading_shift}", runs(k, gray)))
            elif k.name == "li":
                seq.append(("bullet", runs(k, gray)))
            elif k.name == "ul":
                walk(k)
            elif (k.name == "aside" and "callout" in c) or "box" in c:
                seq.append(("box",))
                inner = k.find("div", recursive=False) if k.name == "aside" else k
                kids = [x for x in inner.children if isinstance(x, Tag)]
                if not kids or (len(kids) == 1 and kids[0].name == "p" and blank(kids[0])):
                    seq.append(("blank",))  # an empty box shows one blank line either way
                else:
                    walk(inner)
                seq.append(("end box",))
            elif "column-list" in c or "cols" in c:
                seq.append(("columns",))
                for col in k.children:
                    if isinstance(col, Tag):
                        seq.append(("column",)); walk(col); seq.append(("end column",))
                seq.append(("end columns",))
            elif k.name == "figure" and ("image" in c or "img" in c):
                img = k.find("img")
                seq.append(("image", image_name(img["src"])))
                if CHECK_FILES and not (OUT_DIR / urllib.parse.unquote(img["src"])).exists():
                    raise SystemExit(f"image file missing on the site: {img['src']}")
            elif k.name == "figure" and "link-to-page" in c:
                continue  # Notion sub-page links are intentionally left out
            elif k.name in ("div", "nav", "main", "section", "article"):
                walk(k)
            else:
                raise SystemExit(f"unknown element <{k.name} class={c}> — teach the checker about it")

    walk(container)
    while seq and seq[-1] == ("blank",):  # Notion's trailing empty line
        seq.pop()
    return seq


def plain(seq):
    lines = []
    for b in seq:
        if b[0] == "box":
            lines.append("┌──────── box")
        elif b[0] == "end box":
            lines.append("└────────")
        elif b[0] == "blank":
            lines.append("")
        elif b[0] == "image":
            lines.append(f"[image: {b[1]}]")
        elif b[0] in ("columns", "end columns", "column", "end column"):
            lines.append(f"── {b[0]}")
        else:
            s = ""
            for text, bold, ital, gray in b[1]:
                t = text
                if bold:
                    t = f"**{t}**"
                if ital:
                    t = f"_{t}_"
                if gray:
                    t = f"⟨{t}⟩"
                s += t
            prefix = "#" * int(b[0].split()[1]) + " " if b[0].startswith("heading") else ("• " if b[0] == "bullet" else "")
            lines.append(prefix + s)
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    src_path, out_path = map(pathlib.Path, sys.argv[1:3])
    title_override = sys.argv[3] if len(sys.argv) == 4 else None
    src = BeautifulSoup(src_path.read_text(encoding="utf-8"), "html.parser")
    out = BeautifulSoup(out_path.read_text(encoding="utf-8"), "html.parser")

    problems = []

    t_src = src.select_one("h1.page-title").get_text()
    t_out = out.select_one("h1.title").get_text()
    t_want = title_override or t_src
    if t_want != t_out:
        problems.append(f"title differs:\n  expected: {t_want!r}\n  built:    {t_out!r}")

    a = blocks(src.select_one("div.page-body"), src_gray, src_blank, 0)
    global CHECK_FILES, OUT_DIR
    CHECK_FILES, OUT_DIR = True, out_path.resolve().parent
    b = blocks(out.select_one(".prose"), out_gray, out_blank, 1)  # site headings sit one level lower

    src_path.with_suffix(".txt").write_text(f"# {t_src}\n\n" + plain(a), encoding="utf-8")

    for n, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            problems.append(f"block {n} differs:\n  source: {x!r}\n  built:  {y!r}")
            break
    if len(a) != len(b):
        problems.append(f"block count differs: source {len(a)}, built {len(b)}")

    chars = sum(len(t) for blk in a if len(blk) > 1 for (t, *_) in blk[1])
    paras = sum(1 for blk in a if len(blk) > 1)
    if problems:
        print("MISMATCH")
        print("\n".join(problems))
        sys.exit(1)
    print(f"OK: title + {paras} text blocks, {chars} characters, all formatting identical")


if __name__ == "__main__":
    main()
