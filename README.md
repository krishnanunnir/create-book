# create-book

A [Claude Code](https://claude.com/claude-code) skill that writes and builds ebooks
that read well on Kindle and phones. It can write a beginner-friendly book from
scratch, turn Markdown or a set of web articles into a book, fix a broken EPUB, and
make a cover.

Before writing, it checks three things with you:

1. **Format**: EPUB by default; AZW3, PDF or DOCX if you ask.
2. **Structure**: you approve the outline (parts and chapters).
3. **Chapter 1**: you approve the first chapter's Markdown before it writes the rest.

## Install

```bash
git clone https://github.com/krishnanunnir/create-book.git ~/.claude/skills/create-book
```

Then ask Claude Code for a book, or type `/create-book`.

## Requirements

- [Calibre](https://calibre-ebook.com/) (`ebook-convert`, `ebook-meta`)
- Node.js (`npx`, for percollate when building from web articles)
- Python 3
- Brave or Chrome (covers and phone-width previews)
- macOS `sips` and `xmllint` (the scripts are written for macOS)

## Layout

- `SKILL.md`: the workflow Claude follows
- `references/writing.md`: how chapters get written
- `scripts/`: build (`md-to-epub.sh`, `web-to-epub.sh`), fix, check, lint, cover
- `assets/book.css`: the book stylesheet
