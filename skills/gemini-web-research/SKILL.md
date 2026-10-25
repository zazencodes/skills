---
name: gemini-web-research
description: Use when the user asks to delegate substantial web research to Gemini CLI or agy. Do not invoke for ordinary research requests or a quick search.
---

# Gemini Web Research

Orchestrate web research through interactive `agy` sessions in tmux panes, then use their findings in the parent task. Invoke this skill only when the user asks to use Gemini or `agy` for research, including a clear request to delegate research to Gemini. Do not choose it merely because research is extensive.

## Roles

You are the orchestrator; the `agy` sessions are workers. They do the searching, page reading and distilling. You decide what to ask, read their reports, and decide whether the answer is good enough. Do not run web searches or fetches yourself. If something needs checking, send it to a worker. Your context is for thinking and synthesis, not raw pages.

## Size the research to the need

Research only as much as the parent task needs. Before launching, decide:

- **The decision or answer it feeds.** What will you or the user do with the result?
- **The stop condition.** What does the report need to contain for you to proceed? Once that is met, stop, even if more could be learned.
- **Sessions.** Default to one. Add a parallel session only for an area that is independent of the others and needs its own digging.
- **Effort.** Pick per session:
  - `low`: a few facts, a current value, a link, a quick check.
  - `medium`: a comparison or summary across several sources.
  - `high`: a contested, technical or poorly documented question where shallow results would mislead.

Start at the lowest effort that could meet the stop condition. Escalate only when a report shows the question is harder than expected.

## Workflow

1. **Launch** the sessions you sized. Each prompt states the question, what the answer is for, the stop condition, and the expected report length. Tell the worker not to survey beyond that.
2. **Read each report as it lands.** Check it against the stop condition.
3. **Follow up only on gaps that matter** to the answer: a missing fact you need, a contradiction that changes the conclusion, or a claim too weakly sourced to act on. Do not follow up to make a sufficient answer more complete.
4. **Synthesize** as soon as the stop condition is met.

## Launch a session

The user always works in tmux. Each session runs in a new pane so they can watch it:

```bash
<this skill's directory>/scripts/agy-research.sh <low|medium|high> <scratch>/<area>-1.md 'Research <question>. This is for <purpose>. Stop once you can <stop condition>; do not research beyond it. Keep the report to <length>. Cite direct source URLs beside substantive claims. Distinguish publication dates from event dates. Flag uncertainty. Take no external actions and edit no files except the report. When finished, write the complete report in a single write to <scratch>/<area>-1.md.'
```

The launcher splits the current pane, starts `agy -i` with the Gemini 3.8 Flash model and reasoning effort for the chosen level, prints `started in tmux pane %<id>` to stderr, waits until the report exists, then prints it. Run each launcher as its own background command, without redirecting stderr away, so every session notifies you separately when it finishes and its pane id stays in the output. Record which pane covers which area. If a model is unavailable, check `agy models` and update the launcher to the current Gemini Flash models.

## Follow up in a session

```bash
<this skill's directory>/scripts/agy-followup.sh %<id> <scratch>/<area>-2.md 'Follow-up: <targeted question>. Write the complete answer in a single write to <scratch>/<area>-2.md.'
```

This types the prompt into the pane with `tmux send-keys`, waits for the new report, then prints it. The session keeps its context, so the follow-up can be short. The prompt must be a single line, and each follow-up needs a new report path. Run it in the background like a launch. Send follow-ups only to a session that has finished its last report. A follow-up runs at its session's effort; launch a new session to change effort.

Panes stay open after the turn; the user closes them. If a pane closes before its report is written, the script exits with an error: report it rather than silently switching research services.

## Use the result

Before repeating a claim the user will act on, make sure its source supports it. If the report's citation is weak or the claim is surprising, have a worker open the link and confirm. Return a synthesis with links, not raw Gemini reports.
