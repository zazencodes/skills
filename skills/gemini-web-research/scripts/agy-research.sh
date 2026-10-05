#!/usr/bin/env bash
# Run an agy research prompt interactively in a new tmux pane, then print the report it writes.
#
# Usage: agy-research.sh <report.md> <prompt>
#
# The pane stays open after the turn so the user can read or continue the session.
# Exits non-zero if the pane closes before the report exists.
set -euo pipefail

[ $# -eq 2 ] || { echo "usage: agy-research.sh <report.md> <prompt>" >&2; exit 2; }
report_dir="$(cd "$(dirname "$1")" && pwd)"
report="$report_dir/$(basename "$1")"
[ ! -e "$report" ] || { echo "agy-research: report already exists: $report" >&2; exit 1; }

pane=$(tmux split-window -h -P -F '#{pane_id}' -c "$PWD" \
  agy --model gemini-3.8-flash-high --effort high --add-dir "$report_dir" -i "$2")
echo "agy-research: started in tmux pane $pane; waiting for $report" >&2

until [ -s "$report" ]; do
  tmux display-message -p -t "$pane" '' >/dev/null 2>&1 \
    || { echo "agy-research: pane $pane closed before writing $report" >&2; exit 1; }
  sleep 5
done
sleep 2  # let the write finish
cat "$report"
