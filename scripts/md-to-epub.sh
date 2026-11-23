#!/bin/sh
# Markdown -> Kindle-friendly EPUB with Calibre.
# Usage: md-to-epub.sh book.md "Title" "Author" [cover.jpg] [out.epub]
# Page breaks only before h1 (Calibre's default also breaks before every h2, which
# leaves near-empty pages on Kindle). An h1 directly after a "Part ..." h1 shares its page.
set -e
MD="$1"; TITLE="$2"; AUTHOR="${3:-Unknown}"; COVER="$4"; OUT="${5:-${MD%.*}.epub}"
CSS="$(cd "$(dirname "$0")/.." && pwd)/assets/book.css"
set -- "$MD" "$OUT" --input-encoding utf-8 --formatting-type markdown --paragraph-type off \
  --markdown-extensions "tables,fenced_code,toc" --extra-css "$CSS" \
  --title "$TITLE" --authors "$AUTHOR" --language en \
  --level1-toc //h:h1 --level2-toc //h:h2 --chapter "//h:h1" --chapter-mark none \
  --start-reading-at "//h:h1" \
  --page-breaks-before "//h:h1[not(preceding::h:h1[1][starts-with(normalize-space(.),'Part ')])]"
[ -n "$COVER" ] && set -- "$@" --cover "$COVER"
ebook-convert "$@" | tail -1
