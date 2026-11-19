# zazencodes-skills

## 0.5.0

### Minor Changes

- [`8f74ae4`](https://github.com/zazencodes/skills/commit/8f74ae48a21dcb609312b58845c67eca093703fe) Thanks [@zazencodes](https://github.com/zazencodes)! - adr: new skill that reads a project's Architecture Decision Records before changing an area and writes one whenever a real decision is made.

- [#6](https://github.com/zazencodes/skills/pull/6) [`ea810a4`](https://github.com/zazencodes/skills/commit/ea810a4b027c892b48d4411a20966b12c1249444) Thanks [@zazencodes](https://github.com/zazencodes)! - ascii-viz: add a linked pattern gallery with reusable diagrams for usage, progress, timelines, flows, comparisons, choices, architecture, and status. Each pattern includes guidance for adapting illustrative examples to verified data.

- [`c4325d2`](https://github.com/zazencodes/skills/commit/c4325d296e6561e97e6aa8c93e30b95c69f3e22d) Thanks [@zazencodes](https://github.com/zazencodes)! - humanizer-tryhard: use focused, example-based references and reuse them across the same ordered editorial rounds. Add maintenance guidance for reviewing upstream changes and keeping the pass guides current.

- [`b775c49`](https://github.com/zazencodes/skills/commit/b775c491d02001377cfda58dbed71e01f0ca9327) Thanks [@zazencodes](https://github.com/zazencodes)! - humanizer-tryhard: add rigorous drafting and editing with two full rounds of focused review, a final skeptical read, and a bundled Wikipedia reference that refreshes every seven days while preserving the last good copy offline.

- [#10](https://github.com/zazencodes/skills/pull/10) [`9b4e4ef`](https://github.com/zazencodes/skills/commit/9b4e4ef3d873ddd2a5632dbc3438141e4b9864bc) Thanks [@zazencodes](https://github.com/zazencodes)! - japanese-only: add an opt-in conversation mode that keeps replies in Japanese until explicitly disabled, while preserving technical literals and required output contracts.

- [`ede3a0a`](https://github.com/zazencodes/skills/commit/ede3a0a47f60b12e209285ec82db6c09a75cc0fb) Thanks [@zazencodes](https://github.com/zazencodes)! - tavily-text: new skill for display type whose letters alternate between Geist Pixel Square and Newsreader Italic inside each word, with font, letter-choice, sizing and colour rules.

- [`2be4dc6`](https://github.com/zazencodes/skills/commit/2be4dc6cbf1d5a66ea09ab9cc7f9d9b71fd75b43) Thanks [@zazencodes](https://github.com/zazencodes)! - terminal-explainer: review a change in an illustrated terminal walkthrough, inspect captured source or diffs, and send structured feedback to the agent. Inside tmux the reader opens in its own pane, works entirely from the keyboard, uses the terminal's colors and draws figures with Kitty graphics in Ghostty and kitty. Choose a local image generator and optionally run illustration jobs in tmux-agent-plane.

### Patch Changes

- [`a174880`](https://github.com/zazencodes/skills/commit/a174880c01c405b1e45053066e5aca7399bb9494) Thanks [@zazencodes](https://github.com/zazencodes)! - gemini-web-research: research jobs now run on Gemini 4 Hydrogen at high effort.

- [`d257f1a`](https://github.com/zazencodes/skills/commit/d257f1ae2dc7f40b0a789d4b8457d23c23f5ea0e) Thanks [@zazencodes](https://github.com/zazencodes)! - japanese-only: shorten the discovery description while keeping both invocation forms and the conversation scope.

- [#9](https://github.com/zazencodes/skills/pull/9) [`0ab8a18`](https://github.com/zazencodes/skills/commit/0ab8a18c3c57377e88f05a2440363197105f8880) Thanks [@zazencodes](https://github.com/zazencodes)! - adr, ascii-viz, codex-image-gen, gemini-web-research, git-commit-conventions, init-agents-md, inspo-swipe-list, random-number-generator, tldr: shorten discovery and Codex UI descriptions while retaining activation rules and routing restrictions.

## 0.4.0

### Minor Changes

- [`f74a981`](https://github.com/zazencodes/skills/commit/f74a9819823fd32c14dcc46bec4bf848ef00e23f) Thanks [@zazencodes](https://github.com/zazencodes)! - ascii-viz: new skill that answers with ASCII diagrams and charts, drawn only where a picture explains faster than prose.

- [`68cd364`](https://github.com/zazencodes/skills/commit/68cd364f11092efbdb375d604589a09ed838883a) Thanks [@zazencodes](https://github.com/zazencodes)! - gemini-web-research: research now runs as parallel Gemini jobs instead of sessions in tmux panes, and tmux is no longer required. A script checks each job's trace and every claim's quote against the pages it read, and the skill picks how many jobs to run from how hard the question is.

### Patch Changes

- [`f099bbe`](https://github.com/zazencodes/skills/commit/f099bbe150596a060b23b90ac9f655ac2bc81bc2) Thanks [@zazencodes](https://github.com/zazencodes)! - tldr: only add a session footer when the reply is at least twice as long as the TLDR would be, so a TLDR is never longer than the text above it. Explicit summary requests are still answered.

## 0.3.0

### Minor Changes

- [`3ccd756`](https://github.com/zazencodes/skills/commit/3ccd756ab5120f6a6665e467f30c41f0f721e435) Thanks [@zazencodes](https://github.com/zazencodes)! - inspo-swipe-list: new skill that draws on a saved design inspiration swipe list, asks which entries to use, and adds new finds to it.

- [`a6d4ce0`](https://github.com/zazencodes/skills/commit/a6d4ce0b466486ee75ec69e51c1560c13d02c1a7) Thanks [@zazencodes](https://github.com/zazencodes)! - tldr: new skill for brief, structured summaries of outcomes, decisions, open questions and next steps. Invoke with TLDR, /tldr or $tldr to summarize the previous reply and enable separated TLDR footers for the session, with one-reply and stop controls.

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
