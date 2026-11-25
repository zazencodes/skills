---
name: diagram-viz
description: Draw diagrams and timelines as images in the ZazenCodes style. Use for architecture or block diagrams, how-something-works pictures and flows; not for data charts or ASCII.
---

# Diagram Viz

Explanatory diagrams in the ZazenCodes style: HTML and CSS on a fixed 1280×720 frame, rendered to PNG with headless Chrome. The look is quiet gunmetal boxes on a dark page, a brand-coloured outline only on the entities that matter, thin grey arrows, and every element named in plain text. Draw it in this HTML. Mermaid, Graphviz, chart libraries and image generators cannot produce this style.

Requirements: macOS, Google Chrome, and the fonts Inter and JetBrainsMono Nerd Font installed (`brew install --cask font-inter font-jetbrains-mono-nerd-font`).

The target look is `examples/harness.png` (block diagram) and `examples/timeline.png` (timeline), each beside the HTML that made it. View the matching PNG and read its HTML before you draw.

`<skill>` below is this skill's directory.

## Procedure

Work in this order. Colour comes last.

1. **Pick the form** from the table below. If the content is numbers to compare, it is a chart and not for this skill.
2. **Write the words.** Give each box a label of 1 to 3 words, a short muted sublabel, and at most one more muted line of detail. Name every element in text: no legend, and nothing that colour alone explains. Keep it to about 15 labelled pieces, counting boxes, chips and rows; more means two diagrams.
3. **Lay it out.** Copy `<skill>/template.html` to `<name>.html` where the user wants the image (the current project if they named no place). Set the `<title>` and `<h1>`, set the `.dg` height to what the diagram uses (at most 480px), and place components inside `.dg` with absolute `left`, `top`, `width` and `height` in whole px, following *Geometry*. A short diagram is fine: the frame centres it, so don't stretch boxes to fill the space.
4. **Colour by job.** Every box starts neutral. Then give purple to the subject, the thing the title is about, and orange to its main counterpart (see *Palette*). If the subject contains other parts, make it a key box holding them as chips or rows; a dashed group never takes an accent. A timeline's dots are purple and nothing else is coloured.
5. **Render:** `<skill>/scripts/render.sh <name>.html <name>.png`. It writes a 2560×1440 PNG, then checks the layout. If something is wrong it exits 1 and lists the faults: text that wraps where it must not, content overflowing a box, text colliding with text, lines or boxes, arrows touching boxes, and anything outside the canvas or frame. It also fails if Chrome, Inter or JetBrainsMono Nerd Font is missing. Fix every fault and render again.
6. **Look at the PNG** with your image-viewing tool (the Read tool in Claude Code). The check catches geometry; you judge the picture. Does it explain the idea at a glance? Do the boxes line up and the gaps match? Does it look like the matching example? Fix and re-render until it does.

Deliver both files, the PNG and its HTML source.

## Pick the form

| The diagram shows | Form | Components |
|---|---|---|
| What talks to what | Boxes joined by arrows | `.box`, `.arr`, `.varr`, `.cap` |
| What a thing is made of or holds | Its parts or contents as chips inside it | `.chips` |
| A thing's parts, each with a description | Rows stacked inside its box | `.rows` |
| What belongs together | Dashed outline with a caption | `.group`, `.cap` |
| A whole that is the sum of parts | Bracket under the parts, "A = B + C" below | `.bracket`, `.sum` |
| The things one entity uses | Column of boxes on a spine | `.spine`, `.item` |
| Steps in order | Boxes left to right with arrows | `.box`, `.arr.r` |
| When things happened | Axis with dated events | `.axis`, `.ev` |

Forms combine: the harness example uses five of them.

## Palette

The template defines these as CSS variables at the top of its component block. Use no other colours.

| Token | Hex | Job |
|---|---|---|
| `--zc-bg` | `#1b2023` | Page |
| `--zc-surface-code` | `#262c2f` | Box fill |
| `--zc-border` | `#414a4f` | Box and chip borders |
| `--zc-rule` | `#4e575c` | Group outline, spine, bracket, timeline axis |
| `--zc-heading` | `#ffffff` | Box titles, event names |
| `--zc-body` | `#f4f5f6` | Chip text, sums |
| `--zc-muted` | `#c6cccf` | Sublabels, captions, arrows |
| `--zc-h2` | `#C6AEFF` | Accent 1, purple: the subject (`.a1`) |
| `--zc-h4` | `#FFA557` | Accent 2, orange: its main counterpart (`.a2`) |
| `--zc-pink` | `#FF2E88` | Accent 3, pink: a third identity, only when one is needed (`.a3`) |

- An accent marks identity and nothing else: a 2px outline on a key box, or the timeline dots. Assign accents in order: purple, then orange, then pink. A diagram with one accent uses purple.
- Text is heading, body or muted, never an accent colour. Arrows and lines stay neutral.
- `scripts/check_palette.py` validated these accents on the page and box colours. Each has at least 4:1 contrast. Every pair stays apart under normal vision (OKLab ΔE ≥ 15) and under protanopia and deuteranopia (ΔE ≥ 8):

  | Pair | Normal | Worst colour-blind | Result |
  |---|---|---|---|
  | purple + orange | 22.5 | 22.4 | pass |
  | purple + pink `#FF2E88` | 26.0 | 17.4 | pass |
  | orange + pink `#FF2E88` | 24.7 | 16.6 | pass |
  | purple + lifted pink `#FF80B5` | 14.8 | 10.5 | fail: never use `#FF80B5` |
  | purple + cyan `#06D6E8` | 18.1 | 3.2 | fail: no cyan |

- If the brand palette changes, re-run the check with the new values and update this table: `python3 <skill>/scripts/check_palette.py --bg "#1b2023" --surface "#262c2f" "#C6AEFF" "#FFA557" "#FF2E88"`. It exits 1 when a pair fails.

## Geometry

The `.dg` canvas is 1136px wide: a 1280px slide with 72px margins.

- **Planning sizes:** text runs about half its font size per character, so 8px a character at 16px and 11px at 21px bold. Line heights are 1.3 × font size: 27px for a 21px title, 21px for a 16px sublabel or caption. A chip is its text width plus 26px, and 36px tall. Box padding is 10px top and bottom, 16px left and right. The render check finds whatever these estimates miss.
- **Boxes:** 1px border, 10px radius. The title `.t` is 21px bold and the sublabel `.s` 16px muted, directly under it; a further detail line is another `.s` with `margin-top: 14px`. A one-line box is 46px tall and uses `.t.small` (19px). A key box adds `.a1`, `.a2` or `.a3`.
- **Spacing:** leave at least 24px between boxes. Boxes in a row share `top` and `height`; boxes in a column share `left`.
- **Arrows:** `.arr` is horizontal (heads `.r`, `.l`), `.varr` vertical (heads `.d`, `.u`); set the length with `width` or `height`. Leave 6px between the arrow element's ends and the boxes it joins. Give an arrow a `.cap` label when its ends don't already say what flows, and centre the label over the arrow's span with about 8px between text and line. Two opposite flows between the same boxes are two arrows, about 60px apart and centred on the boxes' shared middle, with one label above the top arrow and one below the bottom arrow. A double-headed `.arr.l.r` is for a two-way link that needs no label.
- **Groups:** the dashed outline sits 20px outside its children. Its caption goes inside the top-left corner, 20px in and 9px down.
- **Chips:** inside the box after the title, in a `.chips` div. They wrap onto a new row with 10px gaps.
- **Rows:** inside the box after its sublabel, in a `.rows` div. Each row is a plain `<div>` holding a `.t.small` title and an `.s` description, both on one line. Rows are 47px tall and 10px apart, and the titles share a column as wide as the longest.
- **Nesting:** anything inside a box is part of its HTML, as chips or rows, never a separate box laid on top of it. The render check reports text that runs into a box it isn't part of.
- **Bracket:** 12px tall, starting about 20px below the parts it spans. The `.sum` caption sits 8px under it at the same width.
- **Spine list:** a caption 32px above the first item. `.item` boxes are 224×42px on a 52px pitch, their `left` 12px past the spine's `left`; for a list at the right edge that is `left: 912px`. The `.spine` is 2px wide, starts 20px below the first item's top, and is `(n − 1) × 52 + 2` px tall for n items. The ticks draw themselves. An arrow into the spine needs no label.
- **Text:** words that must stay together, like "VS Code", are joined with `&nbsp;`.
- No icons, shadows, gradients, glows or emoji.

## Timeline

- The `.axis` runs across the middle of the canvas. Each `.ev` sets only `left`, the date's position, rounded to whole px: `x = 92 + (date − first) / (last − first) × 952`, measured in days. This keeps every label inside the canvas.
- The first event goes `.up`, then alternate `.down` and `.up`. Events on the same side must sit at least 184px apart; if two are closer, move one to the other side.
- Each event holds a date `.d`, a name `.m` and a note `.n`. Write the date at the precision the story needs: "Sep 2024", or "24 Feb 2025" when days matter. Put the name in `.m` and any status ("research preview", "generally available") in the note. A note may run to two lines of about 26 characters each.
- A canvas height of 280px fits every event the check allows, up to a two-line name with a two-line note.

## In a Marp deck

Put the diagram on the slide itself. The slide's `#` heading replaces the template's `<h1>`. Paste your page's second `<style>` block, the components and their colours, as `<style scoped>`, then the `.dg` div. The diagram is drawn for the page colour `#1b2023`, as on ZazenCodes slides, and the deck's own render command renders it.

## Common mistakes

- Accent colour on text, arrows or most of the boxes. Only the key entities carry it.
- Guessing a width and widening by trial. Plan with the sizes above, then let the render check say what doesn't fit.
- Treating a clean render check as done. The check measures geometry; only looking tells you whether the picture explains the idea.
