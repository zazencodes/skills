# AGENTS.md

## Project Instructions

- Treat this file as the canonical agent context; `CLAUDE.md` only points here.
- This repo publishes Alex's own agent skills. Each one is developed in his private `~/agents` repo, where `skills/SKILL_ORIGINS.toml` marks it `public = true`, and copied here.
- Only skills marked `public = true` belong here. Never add skills with personal details, private context, or third-party skills.
- Do not commit, push, tag, or publish unless the user explicitly asks.

## Repo Shape

- `skills/<skill-name>/SKILL.md` is each skill's instruction file and metadata; bundled scripts and references sit beside it.
- `skills/<skill-name>/agents/openai.yaml` holds Codex UI metadata: `display_name` and a `short_description` of 25 to 64 characters.
- `.claude-plugin/plugin.json` lists every skill in its `skills` array; `.claude-plugin/marketplace.json` makes the repo its own plugin marketplace.
- `README.md` lists every skill with its install commands.

## Adding or Removing a Skill

Update `skills/`, the `skills` array in `.claude-plugin/plugin.json`, and the README table together. Bump `version` in `plugin.json` on every release, since Claude Code uses it to decide when installed users get an update.

## Validation

```bash
claude plugin validate . --strict
npx skills@latest add . --list
```
