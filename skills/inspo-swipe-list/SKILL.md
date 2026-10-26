---
name: inspo-swipe-list
description: Alex's inspo swipe list of saved design inspiration. Use when Alex asks to use or add to his swipe list or inspo, or when design work could draw on what he has saved.
---

# Inspo Swipe List

The list lives at `/Users/alex/obsidian/AzathHouse/Areas/Inspo Swipe List.md`
in Alex's Obsidian vault. It holds things he found online that inspire him:
mostly visual design, also how a video, tool or app looks and feels. Entries
are newest first. It is growing, so always read the current file.

## If the list is not available

When you cannot read the file (other machine, sandbox, no access):

- If Alex explicitly asked you to use the swipe list or add to it, stop. Tell
  him you can't reach the list and do not finish the task without it.
- If you loaded this skill on your own because the work could use inspiration,
  give him a one-line warning and carry on without it.

## Using the list for inspiration

1. Read the whole list.
2. Pick the entries relevant to the task. Open their links when the
   description alone isn't enough to work from.
3. If Alex named a specific entry, use it. Otherwise, unless one entry is
   obviously right, ask him which to use with your question-asking tool
   (e.g. `AskUserQuestion`), not in prose. Offer your best single
   suggestion first, marked recommended, then an alternative or a group of
   entries to combine. Keep the options to the entries you found relevant.
   He can always answer with something else.
4. Say which entries you drew on and what you took from each.

## Adding to the list

When Alex says "add this to my swipe list" (a link, plus what he likes about
it):

1. Insert a new entry at the top, directly under the `---` that follows the
   intro, in the existing format:

   ```markdown
   ## YYYY-MM-DD . Short title

   https://link

   One or two sentences on what it is and why Alex likes it, in his words
   where possible.
   ```

   Use today's date. Write the title yourself if he didn't give one. Ask for
   the reason only if he gave none and the link doesn't make it obvious.
2. Commit and push in the vault (`git -C /Users/alex/obsidian/AzathHouse`),
   staging only this file, following the vault's `AGENTS.md` commit
   convention.
