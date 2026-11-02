---
name: tldr
description: Use when the user invokes /tldr or $tldr, sends TLDR or TL;DR as a standalone prompt, or asks to use TLDR for a reply or session. Match case-insensitively. Also applies to later replies while TLDR mode is active.
---

# TLDR

Give the user only what matters, in the fewest clear words. Keep decisions, unanswered questions, and required actions easy to distinguish.

## Activation and duration

- A bare `TLDR`, `TL;DR`, `/tldr`, or `$tldr` summarizes the immediately preceding assistant reply. Output only the TLDR section for that turn.
- If the user names another message or topic, summarize that scope. Use earlier context only to clarify it.
- Any invocation enables TLDR mode for the rest of the conversation, unless the user limits it with wording such as "just this once."
- "Use TLDR for this session" or an opening prompt invoking the skill enables session mode immediately. If there is a task, complete it and append its TLDR.
- While mode is active, answer normally and append a TLDR to each substantive final reply. Progress updates and tool calls need no footer. Even a short final reply gets one; keep it tiny.
- "Stop TLDR" or equivalent ends the mode. Explicit one-reply instructions take precedence for that reply.
- A mention inside quoted text, code, or a discussion about creating this skill is context; activate when the user requests its use.

## What earns a place

Select the facts that change what the user should understand, decide, or do:

- The main outcome or current state.
- Consequential design choices and their practical effect.
- Open questions, blockers, and actions the user must take.
- Material risks, limitations, or missing verification.

Lead with anything requiring the user's attention. Preserve uncertainty and the difference between proposed, completed, and verified work. Include only facts supported by the source. Leave out incidental implementation detail, chronology, repeated context, and filler. Do the requested work fully; brevity applies to the summary.

## Format

In session mode, separate the footer from the normal answer with a blank line, `---`, and another blank line. Use `**TLDR**` followed by a blank line and compact bullets. A standalone summary starts directly with `**TLDR**`.

Aim for 1–4 bullets and about 60 words or fewer. Use fewer when enough; exceed the target only to preserve essential meaning. Use plain language, one idea per bullet, and short labels such as **Decision**, **Question**, **Next**, or **Caution** where they help. Omit empty categories, nested lists, preambles, and closing offers. Preserve a critical link or command when needed to act.

Example footer:

---

**TLDR**

- **Question:** Postmark or SES for email?
- **Next:** Check account deletion on staging; unit tests passed.
- **Decision:** Deleted accounts can be recovered for 30 days.
- **Caution:** Final deletion is irreversible.
