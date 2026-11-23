#!/bin/sh
# Web articles (and local .html section pages) -> EPUB with percollate, then clean it.
# Usage: web-to-epub.sh order.txt "Title" out.epub [cover.jpg]
#   order.txt: one URL or local .html path per line, in reading order.
#   Blank lines and lines starting with # are skipped.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
# Reuse an installed browser, so percollate does not download its own.
if [ -z "$PUPPETEER_EXECUTABLE_PATH" ]; then
  B="$(PYTHONPATH="$DIR" python3 -c 'import _tools; print(_tools.browser())' 2>/dev/null)" \
    && export PUPPETEER_EXECUTABLE_PATH="$B"
fi
grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' "$1" | tr '\n' '\0' \
  | xargs -0 npx -y percollate epub --title "$2" -o "$3"
if [ -n "$4" ]; then python3 "$DIR/fix-epub.py" "$3" --cover "$4"; else python3 "$DIR/fix-epub.py" "$3"; fi
