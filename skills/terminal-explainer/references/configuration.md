# Configure the reader and illustrator

Run `config` to print the effective settings and their file path. Run `config --init` to create an editable file with the defaults. It refuses to overwrite an existing file. Settings live at `$XDG_CONFIG_HOME/terminal-explainer/config.json`, normally under `~/.config`.

| Setting | Meaning |
| --- | --- |
| `presentation` | `terminal` reads in the current TTY. `plane` opens a task in the Agent Plane sidebar. |
| `renderer` | `auto` uses the image protocol reported by the terminal. `cells` draws pictures with colored half-blocks, useful inside a multiplexer. |
| `image_height` | Number of terminal rows available for each figure, from 6 to 40. |
| `illustration_style` | The illustrator's visual direction. Apply it to agent-authored images too. |
| `image_command` | Executable and arguments for a local image generator. An empty array leaves artwork to the author. |

The command gets two whole arguments substituted verbatim, `{prompt}` and `{output}`. It must finish after writing a PNG at the supplied output path and exit nonzero on failure. Configure a command the user chose. Only the illustration brief and style are sent to it. Project code belongs in the brief only when appropriate for that generator.

For the `codex-image-gen` companion skill, put the real absolute path to its installed script in the array. Running this generator uses its configured Codex account.

```json
{
  "presentation": "plane",
  "renderer": "cells",
  "image_height": 16,
  "illustration_style": "One scene, two states. Large shapes and a clear direction of movement.",
  "image_command": ["python3", "/absolute/path/to/codex-image-gen/scripts/codex_image.py", "--prompt", "{prompt}", "--output", "{output}"]
}
```

Write a brief that describes the verified behavior (see [examples/brief.txt](../examples/brief.txt)). In particular, specify the actors, the order of operations, the visual distinction between states, and no embedded text. To run a background illustration job while authoring the tour:

```sh
uv run --script "$EXPLAIN" illustrate brief.txt handoff.png --plane
```

The output names the Agent Plane task and its intended file. Use `tmux-agent-plane task list --json` for its exit status and `tmux-agent-plane task read <task>` for diagnostics. An exited task with code 0 has finished. Inspect the image before adding it to a page. Remove the finished task with `tmux-agent-plane task stop <task>`. Omit `--plane` to render synchronously. The command publishes a verified PNG once and refuses to overwrite an existing output. The generator never runs just because someone opens a walkthrough.
