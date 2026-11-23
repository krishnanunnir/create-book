---
name: create-book
description: Write, build, clean up, verify and add covers to ebooks (EPUB by default; AZW3, PDF or DOCX on request) that read well on Kindle and phones. Use when the user wants to write a book, or the user wants to turn Markdown, notes, a guide or a set of web articles/blog posts into an EPUB, send a book to Kindle, fix an existing EPUB (blank pages, broken images, flat table of contents, cluttered articles, wide code), or make a book cover.
---

# Books for Kindle and phones

A finished book has to do three things:

1. **Teach.** The reader can't stop the book to ask a question, so the text has to
   answer each one before it comes up. When Claude writes the content, read
   `references/writing.md` before any chapter. It builds the whole writing process
   from that one fact: brief, outline (approved by the user), one chapter at a time,
   edit pass, reader test, whole-book pass. Write for a true beginner in the topic
   and build each idea by hand from a tiny working version; a draft pitched at a
   "quick, competent" reader was too high-level to learn from.
2. **Survive the device.** A Kindle or a phone is a small screen with a limited
   renderer. Most broken-book bugs come from a desktop assumption that fails there.
   §1 lists what the device does and the rules that follow from it.
3. **Be safe to share.** No local paths leak, and no fact, date or quote is invented.

Every step below serves one of these. When a rule doesn't fit a case, go back to its
reason.

## 0. Before writing: three checkpoints with the user

Stop at each one and wait for the user's answer. Don't skip one because the request
looks clear.

1. **Format.** Ask which format they want. Default to EPUB (Kindle, Apple Books,
   most phone readers) if they have no preference. Others: AZW3 (older Kindles),
   PDF (print, fixed layout), DOCX (editing). The book is always built and checked as
   EPUB first, then converted in §5.
2. **Structure.** Show the outline: Parts, chapters in order, and what each chapter
   teaches (`references/writing.md` §3). Revise until the user approves it.
3. **Chapter 1.** Write only chapter 1 as Markdown (`md/01.md`), show it, and revise
   until the user approves it. It sets the voice, depth and length for the rest, so
   write no other chapter before this approval.

For a web-article collection, the structure to approve is `order.txt` and its Parts,
and there is no chapter 1 to write. For fixing an existing EPUB, ask only the format.

## Scripts and tools

The scripts are in the `scripts/` folder next to this file. The commands below write
it as `$SKILL`, which stands for this skill's base directory (for a personal install,
`~/.claude/skills/create-book`). Replace it with the real path when you run them.

They need:

- Calibre (`ebook-convert`) to build and convert books;
- Python 3;
- `npx` (Node.js) to fetch web articles with percollate;
- Brave, Chrome, Chromium or Edge for covers and previews. Set `BOOK_BROWSER` to the
  browser's path if it isn't found;
- `sips` (built into macOS) or ImageMagick to convert images;
- `xmllint` to validate XML. Without it, `check-epub.py` skips that check and says so.

If a tool is missing, tell the user which one and how to install it. Don't work
around a missing Calibre with another converter: the page-break and TOC rules below
depend on its options.

## 1. What the device does, and what follows

| The device… | So… |
|---|---|
| fits about 52 monospace characters on a phone line | keep code and diagram lines ≤ 52 chars |
| wraps a long code line back to column 0 | a wrap breaks a diagram, so shorten the line |
| starts a page wherever the build puts a break | break only at chapters, or pages come out near-empty |
| is navigated by its table of contents | give sections `##` headings, nest chapters under Parts |
| shows only JPEG, PNG and GIF | convert AVIF and WebP, fix wrong extensions |
| loses SVG and complex HTML in Calibre's Markdown path | draw diagrams as text in ```` ```text ```` blocks |
| has a narrow column | prefer tables with 2–3 columns |
| is often e-ink, so grayscale | keep the cover title's contrast high |

Ways to fit 52 characters:
- Stack side-by-side boxes vertically.
- Split shell commands with `\`.
- Put code comments on their own line.
- Format Python with `black -l 50`.
- Fix only your own code. Leave quoted third-party code as it is.

## 2. Build: pick the path by where the text comes from

### Markdown (books Claude writes)

```bash
$SKILL/scripts/md-to-epub.sh \
  book.md "Title" "Author" cover.jpg out.epub
```

- One `# h1` per chapter. Only an h1 starts a new page.
- A `# Part N: ...` h1 makes a part page, and the chapter h1 right after it shares
  that page. So don't start an ordinary chapter title with the word "Part ".
- `## h2` marks a section. It shows in the TOC but doesn't start a page. Calibre's
  default breaks before every h2, and the script turns that off.
- Write long books as `md/01.md`, `md/02.md`… and `cat` them together. Save that
  command in a small build script next to the sources, so every rebuild repeats it.
- For a book that isn't in English, set the language: `BOOK_LANG=de md-to-epub.sh …`.
- Before building, run `python3 $SKILL/scripts/lint-md.py md/*.md`. It flags wide
  code lines, long paragraphs, long stretches with no heading and stock phrases.

### Web articles (collections)

```bash
$SKILL/scripts/web-to-epub.sh \
  order.txt "Title" out.epub cover.jpg
```

`order.txt` lists one URL or local `.html` file per line, in reading order. Blank
lines and lines starting with `#` are skipped. Local HTML files make good intro and
"Part N: ..." divider pages. Start each one with `<title>Part 1: Foundations</title>`
and an `<h1>`.

Some sites block automated fetchers. If a page fails, skip it and list it as "link
only" on its Part page. Don't work around the block.

Web pages carry clutter a book doesn't want: "Subscribe to newsletter", "Back to
blog", "Follow us on…", cookie notices, "Related posts", and site suffixes on titles.
After the build, read the start and end of each article's text, then remove what you
find:

```bash
python3 $SKILL/scripts/fix-epub.py \
  out.epub \
  --strip-suffix " | Vantage" \
  --strip-suffix " - Snap Engineering" \
  --junk '<section data-testid="sdsm-block-ctas">.*?</section>'
```

Keep these flags in the project's build script. `web-to-epub.sh` already runs
`fix-epub.py` once, and running it again is safe. Every run:
- converts AVIF, WebP and wrongly named images to PNG, and fixes OPF media types;
- removes the `Source: file:///...` lines percollate adds to local pages, which leak
  the user's paths;
- nests a flat TOC under its "Part" entries;
- with `--cover`, replaces the cover image.

`fix-epub.py` also repairs an EPUB someone else made. It changes the file in place,
so work on a copy.

## 3. Cover

```bash
python3 $SKILL/scripts/make-cover.py \
  spec.json cover.jpg
```

It renders a 1600×2560 JPEG, Kindle's recommended size: a dark background, a large
serif title, a one-line promise and a timeline. Example `spec.json`:

```json
{"accent": "#2dd4bf", "kicker": "A FIELD COLLECTION",
 "title": "Temporal<br>Engineering<br>Blogs",
 "sub": "How real teams run durable workflows in production, in their own words.",
 "events": [["2021", "Snap  microservice reliability"], ["2024", "Netflix  the Temporal platform"]],
 "foot": "Foundations · Origins · Big companies · Migrations"}
```

- Only `title` is required. Leave `events` out when the book has no real sequence to
  show; the cover is then title, promise and footer.
- Take the timeline rows from the book's real content: chapter milestones, the
  running example's steps, or sources with real dates. Never invent dates.
- Two spaces after a name make the name bold. `!!` at the start of an event shows it
  in red.
- Break the title with `<br>` so no line is much over 11 letters. Longer lines are
  shrunk to fit, which makes the whole title smaller.
- For a series, keep the layout and change only `accent`.
- Look at the result: Read `cover.jpg`. Fix anything uneven.
- Markdown builds take the cover as `md-to-epub.sh`'s fourth argument. Web builds take
  it through `web-to-epub.sh` or `fix-epub.py --cover`.

## 4. Verify (always)

A build that finished is not yet a book that works. Check it two ways.

**Mechanically:**

```bash
python3 $SKILL/scripts/check-epub.py out.epub
```

It exits 1 on hard problems: mimetype not first in the zip, a wrong image format or
media type, missing files, `file:///` leaks, invalid XML, and duplicate TOC
`playOrder` values. It also reports things to judge yourself: near-empty pages, wide
code lines, the TOC tree and the cover size.

**By eye, at phone width.** `check-epub.py` numbers the pages. Screenshot at least the
first chapter, and every page that has a diagram or a table:

```bash
python3 $SKILL/scripts/preview-epub.py out.epub 3 --out shot.png
```

Then Read `shot.png`. The shot is 360 pixels wide and 1300 tall.

- `--scroll 1300` moves the window down the chapter. Step through a long one.
- `--scale 2` gives a sharper image. Use it to check diagram alignment: at 1x,
  downscaling can make box borders look misaligned when they are fine.

## 5. Deliver

- If the user chose a format other than EPUB, convert the checked EPUB with Calibre:
  `ebook-convert out.epub out.azw3` (or `.pdf`, `.docx`). For PDF, add
  `--paper-size a5 --pdf-default-font-size 14`. Open the result and look at a
  chapter, since `check-epub.py` only checks the EPUB.
- Put the final book files in one `Final/` folder and give the user that path.
- Keep sources, build scripts, `spec.json` and covers in `build-files/` next to it.
- Send to Kindle takes EPUB by email (50 MB limit) or through the Send to Kindle app.
