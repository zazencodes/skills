# Terminal Explainer design

The reader should be able to answer three questions after a review. What changes for someone using the software? Where does the code establish that? What still needs a decision?

## The review loop

1. The authoring agent follows one representative input through the change. It selects a few scenes, writes the illustration brief and identifies the relevant diff or source range.
2. A configurable illustrator turns the brief into a local image. It can run as a tracked Agent Plane task while the author checks the source. The author inspects the finished picture before opening the tour.
3. The CLI captures the exact image, source and diff into a private run directory. The terminal reader shows each scene with its caption and lets the reviewer expand the evidence in place.
4. The reviewer submits choices and comments. The reader saves one complete JSON response. The calling agent can wait for it or recover it from the run directory after a restart.

## Integration choices

| Component | Responsibility |
| --- | --- |
| Skill | Select a review story, author an accurate brief, verify the visual and interpret the feedback. |
| Bundled CLI and reader | Validate the artifact, snapshot the evidence, display the walkthrough and persist responses. The installable skill carries its own software. |
| tmux | Host the reader in a focused, zoomed pane split from the agent's. It closes on submit and stays open with the error if the reader crashes. Agent Plane can track an illustration job as a named task. |
| User configuration | Choose the renderer, image size, art direction and image command. Provider credentials stay with the chosen generator. |

The skill is the entry point because the author has the change, the user's question and the surrounding conversation. A generic completion hook knows a turn ended but usually lacks a review story. Teams already producing the JSON spec can call the same CLI from a hook. A new daemon or Agent Plane plugin would duplicate task tracking.

The demo walks through the actual answer-writing code. It ships with its illustration, so someone evaluating the reader can complete a review without connecting a generator. A new tour can use an existing screenshot or a generated picture. The first launch of the Python runtime requires access to its dependencies.

## Distribution

The public skill, CLI, demo and configuration reference ship together under [terminal-explainer](../skills/terminal-explainer/SKILL.md). Install from a checkout with `npx skills@latest add . --skill terminal-explainer`. The public repository's existing changeset workflow handles a future release.
