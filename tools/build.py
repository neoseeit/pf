#!/usr/bin/env python3
"""Build every text page from its Notion export, then check each one word for word.

Add a page: put its export in source/ (with its image folder, if any) and add an entry to PAGES.
Run:        python3 tools/build.py

Per page:
  src     the Notion export in source/
  out     the page file (its URL is /<name without .html>)
  title   (optional) a different title than in Notion
  tag     (optional) small tag above the title
  more    what goes under the page: "spec" = the other spec work cards,
          "range" = the vocal range chips, None = nothing
  hidden  True = link-only: not linked from the homepage, search engines told not to list it

The homepage (index.html) is hand-made; keep its cards in step with SPEC_WORK and VOCAL_RANGE.
"""
import html
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SPEC_WORK = [  # (url, brand, what) — same order as on the homepage
    ("/breakout-spec-launch", "Breakout", "product launch"),
    ("/designfiles", "DesignFiles", "landing copy"),
    ("/kalmm", "Kalmm", "abandoned cart flow"),
]
VOCAL_RANGE = [  # (url, word)
    ("/kalmm", "flow"),
    ("/designfiles", "copy"),
    ("/experience-diet", "essay"),
    ("/duo", "story"),
    ("/commission", "lyrics"),
]

PAGES = [
    dict(src="designfiles.notion.html",     out="designfiles.html",     tag="landing copy",        more="spec"),
    dict(src="kalmm.notion.html",           out="kalmm.html",           tag="abandoned cart flow", more="spec",
         title="abandoned cart for Kalmm"),
    dict(src="duo.notion.html",             out="duo.html",             tag="story",               more="range"),
    dict(src="commission.notion.html",      out="commission.html",      tag="lyrics",              more="range"),
    dict(src="experience-diet.notion.html", out="experience-diet.html", tag="essay",               more="range"),
    dict(src="wavewindow.notion.html",      out="wavewindow.html",      hidden=True),
    dict(src="habitshredding.notion.html",  out="habitshredding.html",  hidden=True),
]


def more_html(kind, out):
    url = "/" + out.removesuffix(".html")
    e = lambda t: html.escape(t, quote=True)
    if kind == "spec":
        cards = "\n".join(f'      <a href="{e(u)}"><strong>{e(b)}</strong><span>{e(w)}</span></a>'
                          for u, b, w in SPEC_WORK if u != url)
        return f'\n  <section class="more">\n    <h2>more spec work</h2>\n    <nav class="work">\n{cards}\n    </nav>\n  </section>\n'
    if kind == "range":
        chips = "\n".join(f'      <a href="{e(u)}">{e(w)}</a>' for u, w in VOCAL_RANGE if u != url)
        return f'\n  <section class="more">\n    <h2>vocal range</h2>\n    <nav class="range">\n{chips}\n    </nav>\n  </section>\n'
    return ""


failed = False
for p in PAGES:
    s, o = ROOT / "source" / p["src"], ROOT / p["out"]
    args = [sys.executable, ROOT / "tools/notion_to_html.py", s, o]
    if p.get("hidden"):
        args.append("--hidden")
    if p.get("title"):
        args += ["--title", p["title"]]
    if p.get("tag"):
        args += ["--tag", p["tag"]]
    more = more_html(p.get("more"), p["out"])
    if more:
        args += ["--more", more]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        print(f"{p['out']:24} {r.stderr.strip()}"); failed = True; continue
    r = subprocess.run([sys.executable, ROOT / "tools/check_text.py", s, o] + ([p["title"]] if p.get("title") else []),
                       capture_output=True, text=True)
    print(f"{p['out']:24} {r.stdout.strip() or r.stderr.strip()}")
    failed |= r.returncode != 0
sys.exit(1 if failed else 0)
