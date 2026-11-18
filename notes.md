# steezy.wav — notes for later

## Versions
Zips: `landing page V#.zip` (full project) and `landing page upload V#.zip` (only what goes on GitHub Pages).
- V13: text spacing now matches Notion on every text page — lines in a box sit tight (line height 1.5, no extra gap between lines) and an empty line is exactly one line of space, so stanzas read as blocks again. experience diet intro changed to "mixing profound ideas with rough language: anything can be over-consumed, causing under-appreciation of life in general" (edited in `source/experience-diet.notion.html`, since the Notion export still has the old line). Stylesheet link bumped to `site.css?v=12`. Breakout page unchanged.
- V12: homepage hero restyled — lavender fade behind the top of the page, big title on three lines ("465K subscribers / and 74M views with / $0.00 in ad spend") with purple gradient numbers, stat blocks fade from white to lavender ("soft rise"). Text colours are now a deep dark purple instead of black on every page. Stylesheet link bumped to `site.css?v=11`. Breakout page unchanged.
- V11: stylesheet renamed to `site.css` and linked as `site.css?v=10`, so browsers can't mix the new pages with a cached old `style.css`. Delete the old `style.css` from the repo a day or two after uploading.
- V10: full redesign in the CV style — CV Sans/CV Display fonts, lavender + purple palette, new homepage (centred hero, stats strip with graphics, card + chip links, dark philosophy block, lavender contact), every text page restyled (labels, placeholders, dividers, "more" section). Breakout page unchanged.
- V9: homepage numbers 465,000+ subscribers / 74,000,000+ views; Breakout piece added to spec work ("product launch * Breakout"); Breakout logo on that page links home.
- V8: removed the steezy.wav bar from the Breakout page again (immersion; the page has its own disclaimer). Concept tab title, favicon and noindex stay.
- V7: /breakout-spec-launch — Breakout concept piece (hand-made page, not from Notion), noindex.
- V6: blinking cursor on every page title (moved to `style.css`); Kalmm page titled "abandoned cart for Kalmm".
- V5: habit shredding rebuilt from the updated export ("how do we adjust?" moved out of the last bullet into its own line).
- V4: two link-only pages, /wavewindow and /habitshredding (not on the homepage, not indexed by search engines); converter now handles images and side-by-side columns.
- V3: browser icon (favicon) from the impossible-triangle logo; blinking cursor now also blinks with Reduce motion on; new file names.
- Browsers cache favicons hard — if the old/no icon still shows after uploading, open the site in a private window or clear the cache.

## Contact form (live via Formspree)
- Fields: email, message. Posts to Formspree form `xyeknwle`: https://formspree.io/f/xyeknwle
- Messages arrive in the inbox of your Formspree account. The visitor's email is the reply-to, so you can just hit reply. The email subject is made from the start of the message: first line only, max 50 characters, cut at a word break, with … when shortened (`subjectFrom` in the script at the bottom of `index.html`).
- Spam trap: a hidden `_gotcha` field that only bots fill in; Formspree drops those.
- Button states: send → sending → sent (fields clear) / try again (text kept).
- After going live: send yourself one test message. If it says "try again", check the Formspree dashboard (form confirmed? domain restrictions?).
- Form settings (email address, spam, allowed domains) are managed in the Formspree dashboard, not in the code.

## Pages
| Card on homepage | Links to | File | Notion page |
|---|---|---|---|
| landing copy * DesignFiles | `/designfiles` | `designfiles.html` | Design More. Admin Less. |
| copy | `/designfiles` | (same page) | |
| abandoned cart flow * Kalmm | `/kalmm` | `kalmm.html` | abandoned cart (site title: "abandoned cart for Kalmm") |
| product launch * Breakout | `/breakout-spec-launch` | `breakout-spec-launch.html` | hand-made concept page (see below) |
| flow | `/kalmm` | (same page) | |
| essay | `/experience-diet` | `experience-diet.html` | experience diet |
| story | `/duo` | `duo.html` | duo |
| lyrics | `/commission` | `commission.html` | commission |

**Link-only pages** (no card on the homepage; only people with the link find them):
| URL | File | Notion page |
|---|---|---|
| `/wavewindow` | `wavewindow.html` (+ `images/wavewindow/`) | wave window |
| `/habitshredding` | `habitshredding.html` | habit shredding |
- They carry `<meta name="robots" content="noindex, nofollow">` so Google & co. don't list them.
- Not secret: anyone with the link can open and forward it, and if the GitHub repo is public the files are visible there. Fine for "unlisted", not for anything confidential.
- To make a page link-only or public: set/remove `hidden=True` in `PAGES` in `tools/build.py` (and add/remove its homepage card).

**Concept / spec mock-ups** (hand-made pages in a brand's look; noindex — Breakout is also linked from the homepage):
| URL | File | Original |
|---|---|---|
| `/breakout-spec-launch` | `breakout-spec-launch.html` | `source/breakout-spec-launch.original.html` |
- Made with `tools/concept_page.py`, which changes only: tab title + link previews ("Concept: … · steezy.wav"), favicon (→ steezy.wav icon), noindex, and (with `--home`) the brand logo links back to stzywav.com. Everything else stays byte-for-byte, including the page's own disclaimer and the "scroll all the way down" menu.
- Rebuild / new one:
  `python3 tools/concept_page.py source/breakout-spec-launch.original.html breakout-spec-launch.html --brand "Breakout" --affiliates "Breakout or Kraken" --tab "Breakout multi-account trading launch" --home '<a aria-label="Breakout logo" class="header__logo" href="#">'`
- Optional `--bar` adds a steezy.wav "concept piece" bar on top. Not used: it breaks the immersion.
- The page is big (≈4.6 MB) because the original embeds its images and fonts; fine for a portfolio piece.

- experience diet: the Notion export contained the essay three times. The page is built from the last group only (intro box (text changed by hand in V13, see version log), empty box, essay, empty box). The untouched export is kept as `source/experience-diet.notion.full.html`.

## Links & hosting (GitHub Pages + Squarespace domain)
- Upload to the repo: `index.html`, the 7 subpages, `breakout-spec-launch.html`, `images/`, `site.css`, `fonts/` and the 3 icon files (`favicon.ico`, `icon-512.png`, `apple-touch-icon.png`). Not needed online: `tools/`, `source/`, `notes.md`.
- GitHub Pages serves `kalmm.html` at `/kalmm`, so the clean links work as-is.
- Custom domain: repo Settings → Pages → Custom domain (this adds a CNAME file), tick "Enforce HTTPS" once it's available.
- DNS at Squarespace: A records on the root domain pointing to GitHub Pages' IPs (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and a CNAME for `www` pointing to `<your-username>.github.io`. Remove Squarespace's default records that clash. Double-check against GitHub's "Managing a custom domain" docs.
- Opening the files straight from your computer, page-to-page links won't resolve; run `npx serve` in the folder to click around locally.

## How subpages are built (text-safe)
Subpages are generated from the Notion HTML exports in `source/`, so no text is ever retyped.
- `python3 tools/build.py` rebuilds every subpage and checks each one against its export: every character, bold, italic, gray, heading level, bullet and blank line. Any difference fails the build.
- New page: put the export in `source/<name>.notion.html` (plus its image folder exactly as Notion exported it, e.g. `source/wave window/`), add an entry to `PAGES` in `tools/build.py` (with `tag` and `more`, or `hidden=True`), run it.
- Images are copied to `images/<page>/`, renamed lowercase-with-dashes and scaled down to max 1600 px wide. The checker confirms every image is in the right spot and the file exists.
- Notion columns become side-by-side columns that stack on phones.
- Different title on the site than in Notion: add `title="…"` to that page's entry in `PAGES` (see kalmm). It's used for the heading, breadcrumb and browser tab, and the checker checks against it.
- The checker also writes `source/<name>.notion.txt`, a readable plain-text copy of each page.
- Regenerating overwrites the pages, so make wording changes in Notion and re-export (or edit the HTML by hand and skip regenerating that page).
- The converter stops with an error on any Notion block it doesn't know yet (toggles, tables, embeds…) instead of dropping it.

## Styles (V10 redesign, CV style)
- **Cache rule:** every time `site.css` changes, bump the number in `site.css?v=…` in `index.html` and `tools/page_template.html`, then run `tools/build.py`. Browsers then fetch the new stylesheet instead of a saved old copy.
- Shared look is in `site.css`: fonts, colours, top bar, cursor, tag, spec work cards, vocal range chips, and everything on the text pages. Homepage-only bits (hero, stats strip, philosophy block, contact panel) are in the `<style>` of `index.html`.
- Colours (top of `site.css`): lavender wash `--wash` #e9e8ff, headlines `--ink` #1b1a20, text `--text` #252228, gray `--mute` #6f6c74 / `--faint` #a5a4a7, panels `--panel` #f7f7f9, purple `--accent` #7d74f2 / `--accent-2` #9896ff (cursor, chips) / `--accent-3` #cfceff, dark block `--night` #1b1a20 → `--night-2` #44436a.
- Text pages: the first box (intro note) sits on the gray panel; other boxes are white cards. The converter marks fully-gray lines so they get their own look:
  - first line of a box (e.g. "after 48 hours") → purple label chip (`p.label`)
  - `[one-word]` like `[chorus]` → chip (`p.marker`)
  - `[two words or more]` like `[cart html with checkout button]` → dashed placeholder box (`p.ph`)
  - any other gray line stays plain gray text
  - an empty Notion box → thin lavender divider (`.box.empty`)
- Under each page: spec pages show the other spec work cards, writing pages show the vocal range chips, link-only pages show nothing. Set per page in `PAGES` in `tools/build.py` (`tag`, `more`); the card/chip lists there (`SPEC_WORK`, `VOCAL_RANGE`) should match the homepage.
- Top bar on text pages: "steezy.wav" (links home) / page name; it turns frosted white once you scroll.


## Font
- CV Display (headlines, numbers: Medium 500, Bold 700) and CV Sans (text: Regular 400, Italic, Medium 500, Bold 700), hosted in `fonts/` as small woff2 files (Latin subset).
- Open source (SIL Open Font License, based on Inter) — keep `fonts/OFL-LICENSE.txt` with the files. No web licence needed. (Helvetica Now is no longer used.)
- Every page title has a blinking purple block cursor (`.cursor` in `site.css`).
- To change fonts later: the `@font-face` lines at the top of `site.css`, plus the preload lines in `index.html` and `tools/page_template.html`.

