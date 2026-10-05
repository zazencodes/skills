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

Update `skills/`, the `skills` array in `.claude-plugin/plugin.json`, and the README table together.

## Changesets and Releases

- Every commit that changes what users get (a skill, its scripts or references, `openai.yaml`, the plugin manifest) includes a changeset in `.changeset/`. Repo-only changes (`AGENTS.md`, CI, `README.md` wording) need none.
- Write it by hand as `.changeset/<short-slug>.md`; `.changeset/README.md` shows the format. Start the description with the skill name (`gemini-web-research: ...`) and say what changed for the user, in a sentence or two.
- Bump: `patch` for fixes and wording, `minor` for a new skill or new behaviour, `major` when a skill is removed or renamed.
- Never edit `CHANGELOG.md` or a `version` field by hand. On each push to `main`, `.github/workflows/release.yml` opens a "chore: version skills" pull request that writes the changelog and bumps `package.json` and `plugin.json` together. Merging it tags `vX.Y.Z` and creates the GitHub release. Merge it only when the user asks for a release.

## Validation

```bash
claude plugin validate . --strict
npm run check-plugin-version
npx skills@latest add . --list
```
