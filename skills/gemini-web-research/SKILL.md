---
name: gemini-web-research
description: Use when the user asks to delegate substantial web research to Gemini CLI or agy. Do not invoke for ordinary research requests or a quick search.
---

# Gemini Web Research

Orchestrate web research through interactive `agy` sessions in tmux panes, then use their findings in the parent task. Invoke this skill only when the user asks to use Gemini or `agy` for research, including a clear request to delegate research to Gemini. Do not choose it merely because research is extensive.

## Roles

You are the orchestrator; the `agy` sessions are workers. They do the expensive work: searching, opening pages, checking links, distilling. You decide what to ask, read their reports, spot gaps and contradictions, and send the next question. Do not run web searches or fetches yourself. If something needs checking, send it to a worker. Your context is for thinking and synthesis, not raw pages.

## Workflow

1. **Split the question.** Break the research into independent areas and launch one session per area, in parallel. Keep each first prompt light and narrow; depth comes from follow-ups.
2. **Read each report as it lands.** Look for what is missing, unverified, thin, out of scope, or in conflict with another report.
3. **Follow up in the same session.** For targeted digging on an area a session already covered (verify these links, go deeper on X, fill the Saturday gap), send the follow-up to that pane. The session keeps its context, so the follow-up can be short.
4. **Spin up new sessions** for unrelated areas, or when a session is gone or confused.
5. **Iterate** until the findings answer the question, then synthesize.

## Launch a session

The user always works in tmux. Each session runs in a new pane so they can watch it:

```bash
<this skill's directory>/scripts/agy-research.sh <scratch>/<area>-1.md 'Research <topic and scope>. Search the web and cite direct source URLs beside substantive claims. Distinguish publication dates from event dates. Flag uncertainty. Take no external actions and edit no files except the report. When finished, write the complete report in a single write to <scratch>/<area>-1.md.'
```

The launcher splits the current pane, starts `agy -i` with Gemini 3.8 Flash at high effort, prints `started in tmux pane %<id>` to stderr, waits until the report exists, then prints it. Run each launcher as its own background command, without redirecting stderr away, so every session notifies you separately when it finishes and its pane id stays in the output. Record which pane covers which area. If the model is unavailable, check `agy models`, choose the current Gemini Flash high model, and update both scripts.

## Follow up in a session

```bash
<this skill's directory>/scripts/agy-followup.sh %<id> <scratch>/<area>-2.md 'Follow-up: <targeted question>. Write the complete answer in a single write to <scratch>/<area>-2.md.'
```

This types the prompt into the pane with `tmux send-keys`, waits for the new report, then prints it. The prompt must be a single line, and each follow-up needs a new report path. Run it in the background like a launch. Send follow-ups only to a session that has finished its last report.

Panes stay open after the turn; the user closes them. If a pane closes before its report is written, the script exits with an error: report it rather than silently switching research services.

## Use the result

Have a worker verify the key cited sources before you repeat consequential claims. Ask it to open each link and confirm it supports the claim. Correct or mark as unverified anything that fails. Return a synthesis with links, not raw Gemini reports.
