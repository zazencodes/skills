# Maintaining the focused references

Read this file when updating the skill or incorporating upstream changes. Routine editing follows SKILL.md and the seven pass guides.

## Reviewed source

The focused guides were prepared against the November 14, 2026 snapshot, Wikipedia revision **1385506285**. Each guide records that revision and its license. The snapshot's fetch timestamp and revision describe the fetched article, not the review status of these guides.

The refresh script continues to check every seven days on invocation. It updates `wikipedia.md` and `refresh-status.json` only. A newer snapshot does not automatically change editorial guidance. Keep these two operations distinct in status reports.

## Updating the guides

1. Save the previously reviewed snapshot outside the skill directory, then run `python3 <skill-directory>/scripts/refresh_source.py --force`. Verify the returned status; a failed fetch is not a source update. Preserve the last good snapshot as the script specifies.
2. Compare the fetched revision with the revision recorded here. If unchanged, no editorial update is required. If changed, read the full article, including caveats, examples, ineffective and historical indicators. Compare it with the reviewed revision using the saved snapshot or its Wikipedia revision permalink. Linked subpages and bibliography entries are optional further reading.
3. Use the coverage map below to assign changed and new material. Include subordinate sections. For each new substantive section, add an explicit destination or a reason it is maintenance-only. Removed or reclassified signs require reviewing existing guidance; do not accumulate obsolete rules.
4. Update affected guides with the relevant explanation, a concrete defective example, a supported repair, and a preservation case explaining when similar prose should stay. Prefer examples that clarify a distinct decision. Preserve caveats, historical status, factual uncertainty, genre differences, and exceptions. Never convert a vocabulary list into a blacklist or impose Wikipedia style on other genres.
5. Read all seven guides together for omissions and contradictions. Keep the two ordered A–G rounds, revision after each pass, factual ledger, findings ledger, conditional third round, and final hostile read. Keep routine reading limited to focused guides, with reuse across rounds. Do not make an updating agent silently rewrite guides during an ordinary editing task.
6. Test on varied briefs: a short reply, an evidence-heavy report with questionable citations, a personal essay with supplied voice samples, and clean copy needing little change. Check invented claims, missing facts, changed certainty, flattened voice, and unnecessary edits. Include a real contrast, a factual three-item list, purposeful repetition, and a necessary qualification. Compare old and new workflows blindly where practical; record quality and actual input/cached/output token usage separately. A smaller reference or one successful rewrite does not establish equivalent quality.
7. Record the revision reviewed in this file and every guide only after completing the coverage review. Update attribution when adapting source prose. Do not label invented teaching examples as Wikipedia quotations. Preserve the source's CC BY-SA attribution and license for adapted references. Run repository validation and the refresh tests; update README descriptions if behavior changed, and add the required changeset. Commit and publish only when authorized.

If the previous snapshot is unavailable, retrieve its recorded revision or perform a complete coverage review of the new snapshot. Do not claim a diff was checked without checking it. If maintenance cannot finish, keep the guides' previous reviewed revision explicit and report the incomplete update.

## Coverage map

Every heading below includes its subordinate sections unless separately assigned. This is maintained once per source review, rather than rebuilt by each editing agent.

| Source section or family | Guide / treatment |
| --- | --- |
| Opening text; Caveats; AI detection tools; Your detection ability | G caveats, applicable throughout |
| Content; significance, legacy and broader trends | A |
| Notability, attribution, media coverage; identification by primary/tertiary sources; online presence | B |
| Superficial analyses; vague connection or association | A |
| Vague attributions and overgeneralization | B |
| Outline-like conclusions; awards and recognition | D |
| Language and grammar; vocabulary; copulatives; all negative parallelisms; list-title leads; rule of three | C |
| Style | E for voice; F for destination formatting |
| Communication intended for the user; all disclaimer eras; phrasal/date/URL placeholders | F |
| Markup irregularities | F |
| Citations; broken links; DOI/ISBN; irrelevant DOI; book pages; unconventional references; tracking parameters; unused references | B for evidence, F for rendering |
| Comment-specific indicators; Edit summaries and all subsections | F; Wikipedia conventions only for that destination |
| Miscellaneous: pronounced style shifts; differences between LLMs | E |
| Miscellaneous: submission statements, maintenance templates, canned user pages, permissions gaming | F; destination-specific |
| Miscellaneous: biases in content | B |
| Signs of human writing: age and explaining editorial choices | G/E caveats; authorship investigation is outside routine editing |
| Signs of human writing: syntax | C/E |
| Ineffective indicators | E/G; no isolated-style authorship conclusions |
| Historical promotional language | A/C; retain historical status |
| Historical knowledge cutoffs, prompt refusal, abrupt cutoffs, access dates | F |
| Historical section summaries | D |
| Historical em dashes | E; no punctuation ban |
| Historical lexical diversity/elegant variation | C/E |
| See also, Notes, References, Further reading, External links; search links | Maintenance context; inspect notes for caveats, retain provenance; linked reading optional |

## Cost regression check

Measure the focused guides' combined size and inspect an agent's actual reads. All seven guides should be read in round one; later rounds reuse their context. Repeated full-snapshot loads, repeated unchanged guide reads, section mapping per deliverable, or shortened/skipped passes indicate a regression. Recovering missing context is legitimate. Preserve distinct examples and exceptions before pursuing further reductions in size.
