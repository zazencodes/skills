# Walkthrough format

A spec has a title and a nonempty list of pages. Each page has a heading and body. Optional fields are image, evidence and question. Keep the first screen understandable in isolation. Prefer a sequence of two to four scenes when a change has several moving parts.

```json
{
  "title": "Review · Recovering an interrupted export",
  "pages": [{
    "heading": "A retry resumes at the last saved row",
    "body": "Suppose the network drops after row 200. The worker reads its checkpoint and requests row 201. Expand the diff to check when it saves the checkpoint.",
    "image": {"file": "checkpoint.png", "caption": "Amber marks the saved rows. Blue marks the rows the worker still needs."},
    "evidence": {"file": "src/export.py", "base": "HEAD"},
    "question": {"id": "retry", "prompt": "Which interruption should the test simulate?", "choices": ["Before saving the row", "After saving the checkpoint"]}
  }]
}
```

- Images are PNG, JPEG or WebP files inside the spec directory. A generated diagram can get ordering or labels wrong. Check it against the actual change and use the caption for the crucial relationship.
- Evidence paths are relative to the explicit `--root` (default: current working directory). `{"file":"src/export.py","start":18,"end":32}` captures an inclusive UTF-8 source range. `{"file":"src/export.py","base":"main"}` captures that file's tracked diff hunks from the resolved local commit to the current working tree, including staged and unstaged edits. Add `"head":"HEAD"` (or another commit ref) to diff between two commits regardless of working-tree state, and add `"start":18,"end":32` to keep only the diff hunks overlapping that line range in the target version. Pass a list of evidence objects when one page connects two places, such as an implementation and its test. For a newly created untracked file, use a line range. Read the captured diff before making a claim.
- Omit `choices` for a multiline text question. Question IDs must be unique. Every question present needs an answer to submit. Frame questions around real review decisions: which edge case to test next, whether a trade-off holds, or what to revise. For a reading-only page, omit `question`.
- Each open gets its own private directory under `$XDG_STATE_HOME/terminal-explainer` (default `~/.local/state/terminal-explainer`), containing the material actually displayed. The answer is saved atomically to `response.json`. Reopening the original spec starts a fresh review.
- In the reader, use `n` and `p` (or `Ctrl+N` and `Ctrl+P`) to move between pages, `j` and `k` to scroll, `f` to expand or close the figure, `e` to toggle evidence, `1`–`9` or Space to select a numbered choice, `a` to focus a text response box, Tab and Enter or the mouse to operate controls, `Escape` to leave a text box, and `q` or `Escape` to close. Back and Next preserve your input. Submit returns the whole walkthrough's answers at once.
