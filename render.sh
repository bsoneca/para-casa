#!/bin/bash
# render.sh <page.html> <out.pdf> — prints an HTML page to an A4 PDF with
# headless Chrome (no headers, footers or URL on the page).
set -euo pipefail
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$(dirname "$2")"
"$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --user-data-dir="$(mktemp -d)" --print-to-pdf="$2" "file://$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" 2>/dev/null
echo "$2"
