# zazencodes-skills

## 0.1.1

### Patch Changes

- 56bbf33: codex-image-gen: recover images only from the exact generation session's saved files, failing clearly when its session ID or images are missing. Match output extensions to the actual image format and validate all variants before writing them.

## 0.1.0

### Minor Changes

- First release, with four skills: `codex-image-gen`, `gemini-web-research`, `git-commit-conventions` and `init-agents-md`. Install them as a Claude Code plugin or with `npx skills@latest add zazencodes/skills`.
