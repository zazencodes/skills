# zazencodes-skills

## 0.3.0

### Minor Changes

- [`3ccd756`](https://github.com/zazencodes/skills/commit/3ccd756ab5120f6a6665e467f30c41f0f721e435) Thanks [@zazencodes](https://github.com/zazencodes)! - inspo-swipe-list: new skill that draws on a saved design inspiration swipe list, asks which entries to use, and adds new finds to it.

### Patch Changes

- [`45c898e`](https://github.com/zazencodes/skills/commit/45c898e58730cd38c271d5fbbca8aafc59215d10) Thanks [@zazencodes](https://github.com/zazencodes)! - inspo-swipe-list: use a home-relative path for the swipe list.

- [`7e0273d`](https://github.com/zazencodes/skills/commit/7e0273d8e1509c84f7b1a038766066d703e5f071) Thanks [@zazencodes](https://github.com/zazencodes)! - inspo-swipe-list: refer to the user instead of Alex.

## 0.2.0

### Minor Changes

- [`b93f542`](https://github.com/zazencodes/skills/commit/b93f54287aed6cf90565132b4825f104ee5a8d33) Thanks [@zazencodes](https://github.com/zazencodes)! - gemini-web-research: size research to the task. The launcher now takes a `low`, `medium` or `high` effort that picks the matching Gemini 3.8 Flash model, sessions default to one, and each prompt carries a stop condition so workers stop once the answer is good enough.

- [`6a309b7`](https://github.com/zazencodes/skills/commit/6a309b7d1458ba2ff1df0d316c3e296da862323a) Thanks [@zazencodes](https://github.com/zazencodes)! - random-number-generator: new skill that generates random integers, floats, weighted choices, shuffles, samples, secure integers and secure hex tokens with a Python standard-library script. It moves here from zazencodes/random-number-skills.

## 0.1.1

### Patch Changes

- 56bbf33: codex-image-gen: recover images only from the exact generation session's saved files, failing clearly when its session ID or images are missing. Match output extensions to the actual image format and validate all variants before writing them.

## 0.1.0

### Minor Changes

- First release, with four skills: `codex-image-gen`, `gemini-web-research`, `git-commit-conventions` and `init-agents-md`. Install them as a Claude Code plugin or with `npx skills@latest add zazencodes/skills`.
