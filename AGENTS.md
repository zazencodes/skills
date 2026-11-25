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
- `tests/` holds unittest coverage for bundled scripts.
- `random-number-generator` mentions passwords only as "random password candidate" or "password entropy"; never say it accepts, stores, transforms, validates or repeats existing credentials, so the Snyk Agent Scan stays clear of W007.

## Adding or Removing a Skill

Update `skills/`, the `skills` array in `.claude-plugin/plugin.json`, the README table and the zstack listing (see zstack below) together. When retiring a skill, keep its instructions in `archive/<name>/instructions.md` and record the reason and any replacement in `archive/README.md`.

## zstack

- [zstack](https://github.com/zazencodes/zstack) is the hub where people pick these skills; Alex's checkout is `~/oss/zstack`. Its `catalog.toml` has a `[[skills]]` entry per skill (`id`, `repo = "zazencodes/skills"`, `path = "skills/<name>"`, a one-line `pitch`, `starter`, `needs`). Its README skill table links each one as `https://github.com/zazencodes/skills/tree/main/skills/<name>`, with the catalog pitch as its description.
- Adding, renaming, moving or archiving a skill here updates zstack in the same piece of work: the catalog entry, the README row, and a line under `## [Unreleased]` in its `CHANGELOG.md`. So does changing what a skill does or needs, once its pitch or `needs` stop fitting. Follow zstack's own `AGENTS.md`.
- Push this repo first so the new paths exist, then push zstack. Open every changed link signed out and confirm it loads.
- Skills are written in Alex's private `~/agents` repo and copied here. Its `AGENTS.md` points back to this section.

## Changesets and Releases

- Every commit that changes what users get (a skill, its scripts or references, `openai.yaml`, the plugin manifest) includes a changeset in `.changeset/`. Repo-only changes (`AGENTS.md`, CI, `README.md` wording) need none.
- Write it by hand as `.changeset/<short-slug>.md`; `.changeset/README.md` shows the format. Start the description with the skill name (`gemini-web-research: ...`) and say what changed for the user, in a sentence or two.
- Bump: `patch` for fixes and wording, `minor` for a new skill or new behaviour, `major` when a skill is removed or renamed.
- Never edit `CHANGELOG.md` or a `version` field by hand. On each push to `main`, `.github/workflows/release.yml` opens a "Version skills" pull request that writes the changelog and bumps `package.json` and `plugin.json` together. Merging it tags `vX.Y.Z` and creates the GitHub release. Merge it only when the user asks for a release.

## Validation

```bash
claude plugin validate . --strict
npm run check-plugin-version
npx skills@latest add . --list
python3 -m unittest discover -s tests
```
