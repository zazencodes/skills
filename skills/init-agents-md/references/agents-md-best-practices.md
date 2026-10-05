# AGENTS.md Best Practices

- Prefer short, developer-style notes over generated essays.
- Keep only information that saves exploration time for an agent.
- Keep `AGENTS.md` minimal and repo-specific: include only the smallest set of requirements agents truly need.
- Do not stuff it with generic overview text; that usually does not help agents find the right files faster.
- Every extra instruction has a cost: extra context can increase exploration/testing and raise inference cost significantly.
- Do not repeat the README unless a detail is agent-specific and easy to miss.
- Always inspect the repository before writing anything.
- Best content to include: exact repo-specific tooling, commands, constraints, and non-obvious conventions the agent would not reliably infer from the repo or docs alone.
- Good content: repo purpose, important directories, real commands, validation expectations, and a few sharp edges.
- Bad content: generic coding advice, long architecture history, exhaustive file trees, repeated tool documentation, and broad overview text.
- If the repository has no meaningful tests or automation, say that plainly.

## Minimal Outline

```md
## Project Instructions

## Repo Shape

## Workflow

## Validation
```
