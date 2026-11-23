#!/bin/sh
# Markdown -> Kindle-friendly EPUB with Calibre.
# Usage: md-to-epub.sh book.md "Title" "Author" [cover.jpg] [out.epub]
# Set BOOK_LANG (e.g. BOOK_LANG=de) for a book that is not in English.
# Page breaks only before h1 (Calibre's default also breaks before every h2, which
# leaves near-empty pages on Kindle). An h1 directly after a "Part ..." h1 shares its page.
set -e
MD="$1"; TITLE="$2"; AUTHOR="${3:-Unknown}"; COVER="$4"; OUT="${5:-${MD%.*}.epub}"
CSS="$(cd "$(dirname "$0")/.." && pwd)/assets/book.css"
set -- "$MD" "$OUT" --input-encoding utf-8 --formatting-type markdown --paragraph-type off \
  --markdown-extensions "tables,fenced_code,toc" --extra-css "$CSS" \
  --title "$TITLE" --authors "$AUTHOR" --language "${BOOK_LANG:-en}" \
  --level1-toc //h:h1 --level2-toc //h:h2 --chapter "//h:h1" --chapter-mark none \
  --start-reading-at "//h:h1" \
  --page-breaks-before "//h:h1[not(preceding::h:h1[1][starts-with(normalize-space(.),'Part ')])]"
[ -n "$COVER" ] && set -- "$@" --cover "$COVER"
command -v ebook-convert >/dev/null || PATH="$PATH:/Applications/calibre.app/Contents/MacOS"
command -v ebook-convert >/dev/null || {
  echo "Calibre not found. Install it from https://calibre-ebook.com (macOS: brew install --cask calibre)." >&2
  exit 1
}
# Through a log file, not a pipe: a pipe would hide a failed build behind tail's exit code.
LOG="$(mktemp)"
ebook-convert "$@" > "$LOG" 2>&1 || { cat "$LOG"; rm -f "$LOG"; exit 1; }
tail -1 "$LOG"; rm -f "$LOG"
