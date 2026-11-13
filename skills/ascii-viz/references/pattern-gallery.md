# Pattern gallery

Reusable layouts for ascii-viz. Choose only what makes an answer clearer;
do not turn every reply into a diagram or box ordinary prose.

All example labels, values, and dates below are illustrative, not live
data. Replace them with verified facts. Use `?` for unknown values; do not
infer missing numbers. Keep diagrams in fenced code blocks and lines at
most 72 characters wide. Unicode bars and box drawing match SKILL.md;
use `#`, `.`, `+`, `-`, `|`, and `->` when plain ASCII is needed.

## Patterns

- [Usage and quota](#usage-and-quota)
- [Progress](#progress)
- [Timeline](#timeline)
- [System flow](#system-flow)
- [Before and after](#before-and-after)
- [Option menu](#option-menu)
- [Architecture](#architecture)
- [Status card](#status-card)

## Usage and quota

Use for a measured amount against a known limit. Label used, remaining,
and total values in the same unit. Each of these ten cells represents 10%.
Do not draw a proportional bar if its total is unknown.

```text
Storage  [██████░░░░]  60%
         60 GB used / 100 GB total / 40 GB left
Quota    ? (limit unknown)
```

## Progress

Use for completed work against a known target, not as an invented time
estimate. Keep blocked or unknown work visible rather than implying done.

```text
Migration  [██████░░░░]  6 / 10 tables (60%)
Done: 6    Remaining: 4    ETA: ?
Next: migrate events
```

## Timeline

Use for ordered dates, milestones, or deadlines. This is an ordering
sketch, not a proportional time scale; say so when spacing is schematic.

```text
Release plan (not to scale)
Nov 02            Nov 06             Nov 12
  |-----------------|------------------|
Kickoff           Review            Release
                  ^ today
```

## System flow

Use for a request, event, or data path. Label arrows when the transfer is
not obvious. Show failures explicitly, without inventing a cause.

```text
[Client] --request--> [API] --lookup--> [Cache]
                       |
                     write
                       v
                      [DB]

Failure: [API] --X--> [Cache]  reason: ?
```

## Before and after

Use to contrast the same process or structure on both sides of a change.
Keep labels comparable; do not imply measured performance improvements
unless measurements exist.

```text
Before                     After
[App] ---> [DB]             [App] ---> [Cache] ---> [DB]
Every read hits DB          Cache misses reach DB
Latency: ?                  Latency: ?
```

## Option menu

Use when the user needs to choose among a few concrete options. State
trade-offs, and mark a recommendation only when the context supports it.
This is a text menu, not a claim that interactive controls exist.

```text
Deployment options
[1] Managed service   Less maintenance; recurring cost
[2] Self-hosted       More control; you operate it
[3] Local only        No public access

Choose based on operations budget and access needs.
```

## Architecture

Use for component boundaries and dependencies, rather than chronological
steps. Label groups and keep relationships directional and unambiguous.

```text
             [Browser]
                 |
+--------- Application ---------+
|              [API]            |
|                |              |
|             [Worker]          |
+----------------|--------------+
                 |
             [Database]
```

## Status card

Use for a compact scan of related operational states. Keep it unboxed
when a box would only decorate prose. Report observed states and mark
unknowns explicitly; do not infer overall health from missing data.

```text
Release readiness
  Tests     PASS
  Build     PASS
  Deploy    BLOCKED  awaiting approval
  Health    ?        not checked
Next: obtain deployment approval
```
