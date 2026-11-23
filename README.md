# create-book

A [Claude Code](https://claude.com/claude-code) skill that writes ebooks and builds
them so they read well on a Kindle or a phone.

Ask Claude for a book on a topic, or hand it your notes or a list of blog posts.
What comes back is a finished book: chapters that teach a true beginner step by step,
a table of contents you can navigate, code and diagrams that fit a small screen, and
a cover.

## What it can do

- **Write a book from scratch.** Claude plans it with you, then writes one chapter at
  a time. Each idea starts from a small worked example, and only then gets its name.
- **Turn Markdown or notes into a book.** One `#` heading per chapter, `##` for
  sections.
- **Collect web articles into a book.** Give it a list of URLs in reading order. It
  removes newsletter boxes, "related posts" and other page clutter.
- **Fix an existing EPUB.** Blank pages, images that don't show, a flat table of
  contents, code lines too wide for a phone.
- **Make a cover.** A 1600×2560 JPEG (Kindle's recommended size) with a title, a
  one-line promise and a short timeline taken from the book's content.
- **Check the result.** A script catches broken files, wrong image formats and leaked
  local paths. Claude also renders a chapter at phone width and looks at it.

## You stay in charge

Before writing anything, Claude stops three times and waits for your answer:

1. **Format.** EPUB by default. AZW3, PDF or DOCX if you ask.
2. **Structure.** You see the outline (parts, chapters, what each one teaches) and
   approve it or ask for changes.
3. **Chapter 1.** You read the first chapter's Markdown and approve it before any
   other chapter is written. It sets the voice, depth and length for the rest.

## Install

```bash
git clone https://github.com/krishnanunnir/create-book.git ~/.claude/skills/create-book
```

Start a new Claude Code session so it picks up the skill.

### Requirements

| Tool | Used for |
|---|---|
| [Calibre](https://calibre-ebook.com/) | building and converting books |
| Python 3 | fixing, checking and linting |
| Node.js (`npx`) | fetching web articles |
| Brave or Chrome | covers and phone previews |
| `sips`, `xmllint` | images and XML (built into macOS) |

The scripts are written for macOS.

## Try it

Type `/create-book`, or just ask:

- "Write a beginner's book on how databases store data on disk."
- "Turn the Markdown files in `notes/` into a Kindle book."
- "Make a book from these five blog posts about Kafka, in this order: …"
- "This EPUB has blank pages and the images don't show on my Kindle. Fix it."
- "Make a cover for my book."

Finished books go in a `Final/` folder. Sources, build scripts and the cover spec go
in `build-files/` next to it, so you can rebuild later.

## Using the scripts directly

They work without Claude too. From `~/.claude/skills/create-book/scripts/`:

```bash
# Markdown to EPUB
./md-to-epub.sh book.md "Title" "Author" cover.jpg out.epub

# Web articles (one URL or .html file per line) to EPUB
./web-to-epub.sh order.txt "Title" out.epub cover.jpg

# Clean up an EPUB: convert images, nest the TOC, strip clutter
python3 fix-epub.py out.epub --strip-suffix " | Site Name"

# Check an EPUB (exits 1 on hard problems)
python3 check-epub.py out.epub

# Review Markdown chapters: length, wide code, stock phrases
python3 lint-md.py md/*.md

# Render a cover from a JSON spec
python3 make-cover.py spec.json cover.jpg
```

To get another format, convert the checked EPUB with Calibre:

```bash
ebook-convert out.epub out.pdf
```

## How it's organised

```text
SKILL.md               the workflow Claude follows
references/writing.md  how chapters are planned and written
scripts/               build, fix, check, lint, cover
assets/book.css        the book's stylesheet
```

## Send to Kindle

Email the EPUB to your Kindle address (50 MB limit), or use Amazon's Send to Kindle
app.
