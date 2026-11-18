#!/usr/bin/env python3
"""
Turn a Notion HTML export into a clean steezy.wav page.

Text is copied character-for-character from the export. Only the markup
changes:

  Notion export                          ->  site markup
  -------------------------------------      -----------------------------
  <aside class="callout">                ->  <div class="box">
  <p> (empty)                            ->  <p class="gap"></p>  (one blank line)
  <p class="block-color-gray">           ->  <p class="d">        (gray = opacity)
  <mark class="highlight-gray">          ->  <span class="d">
  <mark class="highlight-default...">    ->  (unwrapped)
  <strong>, <em>, <br>, <a>              ->  kept as-is
  <h1>/<h2>/<h3>/<h4>                    ->  <h2>/<h3>/<h4>/<h5>
  <ul class="bulleted-list"><li>          ->  <ul><li>
  <figure class="link-to-page">          ->  dropped (Notion sub-page links)
  <div class="column-list"><div column>  ->  <div class="cols"><div class="col">  (side by side, stacked on phones)
  <figure class="image"><img>            ->  <figure class="img"><img>; the image is copied to
                                             images/<page>/ and scaled down to max 1600 px wide

Anything the converter doesn't recognise stops the build with an error, so
nothing can be dropped silently.

Usage:
  python3 tools/notion_to_html.py SOURCE.html OUT.html [--title "Page title"] [--crumb "Page name"] [--hidden]

  --title   use this page title instead of the one in the Notion export

  --hidden  page is only reachable by link: tells search engines not to index it
"""
import argparse
import html
import pathlib
import sys
import re
import urllib.parse

from bs4 import BeautifulSoup, NavigableString, Tag

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "page_template.html"
MAX_IMAGE_WIDTH = 1600

# set in main(): where the export lives, where the page goes, and the page's name
CTX = {}


def copy_image(src_attr):
    """Copy an exported image next to the site (scaled down), return (url, width, height)."""
    from PIL import Image
    rel = urllib.parse.unquote(src_attr)
    src = CTX["src_dir"] / rel
    if not src.exists():
        raise UnknownMarkup(f"image file missing next to the export: {rel}")
    name = pathlib.Path(rel).name.lower().replace(" ", "-")
    out_dir = CTX["out_dir"] / "images" / CTX["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    if im.width > MAX_IMAGE_WIDTH:
        im = im.resize((MAX_IMAGE_WIDTH, round(im.height * MAX_IMAGE_WIDTH / im.width)), Image.LANCZOS)
    im.save(out_dir / name, optimize=True)
    return f"images/{CTX['slug']}/{name}", im.width, im.height


class UnknownMarkup(Exception):
    pass


def classes(el):
    return el.get("class") or []


def is_blank(el):
    return el.get_text().strip() == "" and not el.find("br")


# ---------- inline ----------

def inline(node):
    """Convert inline content. Returns an HTML string."""
    if isinstance(node, NavigableString):
        return html.escape(str(node), quote=False)
    if not isinstance(node, Tag):
        return ""

    inner = "".join(inline(c) for c in node.children)
    name = node.name

    if name == "br":
        return "<br>"
    # a wrapper that only holds a line break is just a line break
    if name in ("mark", "strong", "b", "em", "i") and inner == "<br>":
        return "<br>"
    if name in ("strong", "b"):
        return f"<strong>{inner}</strong>" if inner else ""
    if name in ("em", "i"):
        return f"<em>{inner}</em>" if inner else ""
    if name == "mark":
        c = classes(node)
        if "highlight-gray" in c:
            return f'<span class="d">{inner}</span>' if inner else ""
        if any(x.startswith("highlight-default") for x in c):
            return inner
        raise UnknownMarkup(f"unsupported highlight colour: {c}")
    if name == "a":
        href = html.escape(node.get("href", "#"), quote=True)
        return f'<a href="{href}">{inner}</a>'
    if name in ("code", "s", "u"):
        return f"<{name}>{inner}</{name}>"
    if name == "span" and not classes(node):
        return inner
    raise UnknownMarkup(f"unsupported inline element <{name} class={classes(node)}>")


# ---------- blocks ----------

def gray_role(text, first):
    """What a fully-gray line is, so the page can style it:
    [two words or more] -> placeholder (button, image, testimonial…)
    [one-word]          -> marker ([chorus], [verse])
    first line of a box -> label ("after 48 hours")
    anything else       -> plain gray text"""
    t = text.strip()
    if t.startswith("[") and t.endswith("]"):
        return "ph" if " " in t else "marker"
    return "label" if first else None


def paragraph(p, indent, first=False):
    pad = " " * indent
    if is_blank(p):
        return f'{pad}<p class="gap" aria-hidden="true"></p>'
    block_gray = "block-color-gray" in classes(p)
    other = [c for c in classes(p) if c not in ("", "block-color-gray")]
    if other:
        raise UnknownMarkup(f"unsupported paragraph colour: {other}")
    body = "".join(inline(c) for c in p.children)
    cls = ["d"] if block_gray else []
    all_gray = block_gray or re.fullmatch(r'<span class="d">[^<]*</span>', body) is not None
    if all_gray:
        role = gray_role(p.get_text(), first)
        if role:
            cls.append(role)
    attr = f' class="{" ".join(cls)}"' if cls else ""
    return f"{pad}<p{attr}>{body}</p>"


HEADINGS = {"h1": "h2", "h2": "h3", "h3": "h4", "h4": "h5"}


def block(el, indent):
    pad = " " * indent
    name = el.name
    c = classes(el)

    if name == "p":
        return [paragraph(el, indent)]
    if name in HEADINGS:
        tag = HEADINGS[name]
        body = "".join(inline(ch) for ch in el.children)
        return [f"{pad}<{tag}>{body}</{tag}>"]
    if name == "ul" and "bulleted-list" in c:
        lines = [f"{pad}<ul>"]
        for li in el.children:
            if not isinstance(li, Tag):
                if str(li).strip():
                    raise UnknownMarkup("loose text inside a list")
                continue
            if li.name != "li":
                raise UnknownMarkup(f"unsupported list child <{li.name}>")
            body = "".join(inline(ch) for ch in li.children)
            lines.append(f"{pad}  <li>{body}</li>")
        lines.append(f"{pad}</ul>")
        return lines
    if name == "aside" and "callout" in c:
        content = el.find("div", recursive=False)  # Notion wraps callout text in a div
        kids = [k for k in content.children if isinstance(k, Tag)]
        empty = not kids or (len(kids) == 1 and kids[0].name == "p" and is_blank(kids[0]))
        if empty:  # an empty callout = a divider; it still holds one blank line
            return [f'{pad}<div class="box empty">', f'{pad}  <p class="gap" aria-hidden="true"></p>', f"{pad}</div>"]
        lines = [f'{pad}<div class="box">']
        for i, k in enumerate(kids):
            if k.name == "p":
                lines.append(paragraph(k, indent + 2, first=(i == 0)))
            else:
                lines += block(k, indent + 2)
        lines.append(f"{pad}</div>")
        return lines
    if name == "div" and "column-list" in c:
        lines = [f'{pad}<div class="cols">']
        for col in el.children:
            if not isinstance(col, Tag):
                continue
            if "column" not in classes(col):
                raise UnknownMarkup(f"unsupported child in a column list <{col.name}>")
            lines.append(f'{pad}  <div class="col">')
            for k in col.children:
                if isinstance(k, Tag):
                    lines += block(k, indent + 4)
            lines.append(f"{pad}  </div>")
        lines.append(f"{pad}</div>")
        return lines
    if name == "figure" and "image" in c:
        img = el.find("img")
        if img is None or el.find("figcaption"):
            raise UnknownMarkup("image block without an image, or with a caption")
        url, w, h = copy_image(img["src"])
        return [f'{pad}<figure class="img"><img src="{html.escape(url, quote=True)}" alt="" width="{w}" height="{h}" loading="lazy"></figure>']
    if name == "figure" and "link-to-page" in c:
        print(f"  note: dropped Notion page link '{el.get_text().strip()}'", file=sys.stderr)
        return []
    raise UnknownMarkup(f"unsupported block <{name} class={c}>")


def convert(src_path):
    soup = BeautifulSoup(pathlib.Path(src_path).read_text(encoding="utf-8"), "html.parser")
    title = soup.select_one("h1.page-title").get_text()
    body = soup.select_one("div.page-body")
    kids = [k for k in body.children if isinstance(k, Tag)]

    # Notion always leaves an empty paragraph at the end of a page; drop those.
    while kids and kids[-1].name == "p" and is_blank(kids[-1]):
        kids.pop()

    lines = []
    for k in kids:
        lines += block(k, 6)
    return title, "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("out")
    ap.add_argument("--title", help="page title to use instead of the Notion title")
    ap.add_argument("--crumb", help="breadcrumb label (defaults to the page title)")
    ap.add_argument("--hidden", action="store_true", help="link-only page: ask search engines not to index it")
    ap.add_argument("--tag", help="small tag above the title, e.g. 'abandoned cart flow'")
    ap.add_argument("--more", help="HTML for the section under the page (built by tools/build.py)")
    args = ap.parse_args()

    out = pathlib.Path(args.out).resolve()
    CTX.update(src_dir=pathlib.Path(args.source).resolve().parent, out_dir=out.parent, slug=out.stem)

    try:
        title, body = convert(args.source)
        title = args.title or title
    except UnknownMarkup as e:
        sys.exit(f"stopped: {e}")

    crumb = args.crumb or title
    page = (TEMPLATE.read_text(encoding="utf-8")
            .replace("{{title}}", html.escape(title, quote=False))
            .replace("{{crumb}}", html.escape(crumb, quote=False))
            .replace("{{head_extra}}", '<meta name="robots" content="noindex, nofollow">\n' if args.hidden else "")
            .replace("{{tag_html}}", f'    <span class="tag">{html.escape(args.tag, quote=False)}</span>\n' if args.tag else "")
            .replace("{{more_html}}", args.more or "")
            .replace("{{body}}", body))
    pathlib.Path(args.out).write_text(page, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
