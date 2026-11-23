#!/bin/sh
# Web articles (and local .html section pages) -> EPUB with percollate, then clean it.
# Usage: web-to-epub.sh order.txt "Title" out.epub [cover.jpg]
#   order.txt: one URL or local .html path per line, in reading order.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
BRAVE="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
[ -x "$BRAVE" ] && export PUPPETEER_EXECUTABLE_PATH="$BRAVE"
xargs npx -y percollate epub --title "$2" -o "$3" < "$1"
if [ -n "$4" ]; then python3 "$DIR/fix-epub.py" "$3" --cover "$4"; else python3 "$DIR/fix-epub.py" "$3"; fi
