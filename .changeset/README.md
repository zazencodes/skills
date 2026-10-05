# Changesets

Each file in this folder describes one change for the next release. Add one with `npx changeset`, or write it by hand:

```md
---
"zazencodes-skills": patch
---

gemini-web-research: follow up in the same tmux pane instead of opening a new session.
```

Use `patch` for fixes and wording changes, `minor` for a new skill or new behaviour, and `major` when a skill is removed or renamed. On every push to `main`, the release workflow opens a "chore: version skills" pull request that turns pending changesets into `CHANGELOG.md` entries and bumps the version. Merging that pull request tags the release and publishes it on GitHub.
