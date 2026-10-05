#!/usr/bin/env bash
# Send a follow-up prompt to a running agy research pane, then print the new report it writes.
#
# Usage: agy-followup.sh <pane-id> <report.md> <prompt>
#
# The prompt is typed into the pane as one line, so keep it on a single line.
# Exits non-zero if the pane is gone or closes before the report exists.
set -euo pipefail

[ $# -eq 3 ] || { echo "usage: agy-followup.sh <pane-id> <report.md> <prompt>" >&2; exit 2; }
pane="$1"
report_dir="$(cd "$(dirname "$2")" && pwd)"
report="$report_dir/$(basename "$2")"
[ ! -e "$report" ] || { echo "agy-followup: report already exists: $report" >&2; exit 1; }
case "$3" in *$'\n'*) echo "agy-followup: prompt must be a single line" >&2; exit 2;; esac
tmux display-message -p -t "$pane" '' >/dev/null 2>&1 \
  || { echo "agy-followup: pane $pane does not exist" >&2; exit 1; }

tmux send-keys -t "$pane" -l "$3"
sleep 1
tmux send-keys -t "$pane" Enter
echo "agy-followup: sent to tmux pane $pane; waiting for $report" >&2

until [ -s "$report" ]; do
  tmux display-message -p -t "$pane" '' >/dev/null 2>&1 \
    || { echo "agy-followup: pane $pane closed before writing $report" >&2; exit 1; }
  sleep 5
done
sleep 2  # let the write finish
cat "$report"
