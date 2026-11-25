#!/usr/bin/env bash
# Render a diagram page (1280x720) to a 2560x1440 PNG with headless Google Chrome,
# then check its layout and fonts. Exits 1 with a list of faults if the check fails;
# the PNG is still written so you can look at it. Needs macOS and Google Chrome.
# Usage: render.sh diagram.html diagram.png
set -euo pipefail

[ $# -eq 2 ] || { echo "usage: render.sh diagram.html diagram.png" >&2; exit 2; }
[ -f "$1" ] || { echo "No such file: $1" >&2; exit 1; }

chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$chrome" ] || { echo "Google Chrome not found at $chrome" >&2; exit 1; }

scripts="$(cd "$(dirname "$0")" && pwd)"
html="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
out="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
rm -f "$out"

headless() {
  "$chrome" --headless --disable-gpu --hide-scrollbars --no-first-run \
    --user-data-dir="$work/profile" --window-size=1280,720 --force-device-scale-factor=2 "$@" 2>/dev/null
}

headless --screenshot="$out" "file://$html" >/dev/null
[ -s "$out" ] || { echo "Chrome wrote no image to $out" >&2; exit 1; }
size="$(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixel/ {print $2}' | paste -sd x -)"
[ "$size" = "2560x1440" ] || { echo "Expected 2560x1440, got $size: $out" >&2; exit 1; }
echo "$out ($size)"

{ cat "$html"; echo "<script src=\"file://$scripts/layout_check.js\"></script>"; } > "$work/probe.html"
report="$(headless --dump-dom "file://$work/probe.html" \
  | sed -n '/<pre id="layout-report">/,/<\/pre>/p' | sed -e 's/<[^>]*>//g' -e 's/&amp;/\&/g' -e 's/&quot;/"/g')"
[ -n "$report" ] || { echo "Layout check produced no report" >&2; exit 1; }
[ "$report" = "OK" ] || { printf 'Layout faults:\n%s\n' "$report" >&2; exit 1; }
echo "Layout check: OK"
