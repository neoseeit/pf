#!/usr/bin/env python3
"""
Put a hand-made spec / concept mock-up (a saved .html page) on the site, clearly
labelled so nobody mistakes it for the brand's real page.

What it changes — and nothing else (the rest of the file stays byte-for-byte):
  1. browser tab + link previews say "Concept: … · steezy.wav"
  2. the brand's favicon is swapped for the steezy.wav icon
  3. search engines are told not to list it (noindex, nofollow)
  4. optional (--home): the link given (e.g. the brand's logo) goes back to stzywav.com
  5. optional (--bar): a slim steezy.wav bar on top: "concept piece by steezy.wav ·
     not an official <brand> page · not made by or affiliated with <affiliates>",
     with links to your notes (if --notes is given) and back to stzywav.com.
     Off by default — the mock-ups carry their own disclaimer and the bar breaks
     the immersion.

Usage:
  python3 tools/concept_page.py SOURCE.html OUT.html --brand "Breakout" \
      --affiliates "Breakout or Kraken" --tab "Breakout multi-account trading launch" \
      [--home '<a aria-label="Breakout logo" class="header__logo" href="#">']
      [--bar --notes '<div class="showcase__intro">']

  --home   the exact opening tag of a link (usually the logo) that should lead home.

  --notes  an exact, unique bit of HTML where your own notes/disclaimer start;
           the bar's "read the notes ↓" link jumps there.
"""
import argparse
import html
import pathlib
import re
import sys

BAR_CSS = '''<style id="stzy-concept-bar">
@font-face{font-family:"CV Sans";font-weight:500;font-display:swap;src:url("fonts/CVSans-Medium.woff2") format("woff2")}
@font-face{font-family:"CV Sans";font-weight:700;font-display:swap;src:url("fonts/CVSans-Bold.woff2") format("woff2")}
.stzy-bar{position:relative;z-index:1000;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 14px;padding:10px 16px;background:#fbfaf6;color:#221e1a;
  font:500 14px/1.35 "CV Sans","Helvetica Neue",Helvetica,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;letter-spacing:.01em;text-align:center;-webkit-font-smoothing:antialiased}
.stzy-bar b{font-weight:700}
.stzy-bar .stzy-dot{display:inline-block;width:.5em;height:.78em;margin-right:.45em;vertical-align:-.06em;background:#eba644}
.stzy-bar a{color:inherit;text-decoration:none;opacity:.62;transition:opacity .22s ease}
.stzy-bar a:hover,.stzy-bar a:focus-visible{opacity:1}
</style>
'''
ICONS = ('<link rel="icon" href="favicon.ico" sizes="any">\n'
         '<link rel="icon" type="image/png" sizes="512x512" href="icon-512.png">\n'
         '<link rel="apple-touch-icon" href="apple-touch-icon.png">')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source"); ap.add_argument("out")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--affiliates", required=True)
    ap.add_argument("--tab", required=True, help="short description for the browser tab")
    ap.add_argument("--notes", help="with --bar: exact HTML where your notes start (gets an anchor)")
    ap.add_argument("--bar", action="store_true", help="add the steezy.wav concept bar on top")
    ap.add_argument("--home", help="exact opening <a ...> tag that should link back to the homepage")
    a = ap.parse_args()

    s = pathlib.Path(a.source).read_text(encoding="utf-8")
    e = lambda t: html.escape(t, quote=True)
    tab = f"Concept: {a.tab} · steezy.wav"
    disclaim = f"Not an official {a.brand} page; not made by or affiliated with {a.affiliates}."

    def once(pattern, repl, regex=False):
        nonlocal s
        hits = re.findall(pattern, s) if regex else [pattern] * s.count(pattern)
        if len(hits) != 1:
            sys.exit(f"stopped: expected exactly one match for {pattern[:60]!r}, found {len(hits)}")
        s = re.sub(pattern, lambda m: repl, s, count=1) if regex else s.replace(pattern, repl)

    # 1. tab title + previews
    once(r"<title>.*?</title>", f"<title>{e(tab)}</title>\n"
         f'<meta name="description" content="Concept piece by steezy.wav. {e(disclaim)}">\n'
         f'<meta property="og:title" content="{e(tab)}">\n'
         f'<meta property="og:description" content="Spec work by steezy.wav. {e(disclaim)}">', regex=True)
    # 2. favicon
    icons = re.findall(r'<link\b[^>]*\brel="[^"]*icon[^"]*"[^>]*>', s)
    for tag in icons:
        s = s.replace(tag, "", 1)
    s = s.replace("</head>", ICONS + "\n</head>", 1)
    # 3. noindex
    if not re.search(r'<meta[^>]+name="robots"[^>]+noindex|<meta[^>]+noindex[^>]+name="robots"', s):
        s = s.replace("</head>", '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
    # 4. (optional) logo -> home
    if a.home:
        if 'href="' not in a.home:
            sys.exit("stopped: --home tag has no href")
        once(a.home, re.sub(r'href="[^"]*"', 'href="/"', a.home, count=1))
    # 5. (optional) notes anchor + bar
    if not a.bar:
        pathlib.Path(a.out).write_text(s, encoding="utf-8")
        print(f"wrote {a.out}")
        return
    links = '<a href="/">stzywav.com</a>'
    if a.notes:
        tag = a.notes
        if "id=" in tag:
            sys.exit("stopped: --notes element already has an id")
        once(tag, tag.replace(">", ' id="concept-notes">', 1) if tag.endswith(">") else tag)
        links = '<a href="#concept-notes">read the notes ↓</a> · ' + links
    s = s.replace("</head>", BAR_CSS + "</head>", 1)
    bar = ('<div class="stzy-bar" role="note"><span><span class="stzy-dot" aria-hidden="true"></span>'
           f'<b>concept piece by steezy.wav</b> · not an official {e(a.brand)} page · '
           f'not made by or affiliated with {e(a.affiliates)}</span><span>{links}</span></div>')
    m = re.search(r"<body\b[^>]*>", s)
    if not m:
        sys.exit("stopped: no <body> tag")
    s = s[:m.end()] + bar + s[m.end():]

    pathlib.Path(a.out).write_text(s, encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
