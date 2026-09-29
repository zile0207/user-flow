---
name: ask-project
description: Answer questions about the current user-flow project in conversation. Where things stand, which maps and boards exist and whether they're up to date, which journeys or flows are still missing, what is left to design, which decisions are open and what they block, what to look out for, edge cases worth checking, and where a screen lives. Read-only. Use when the user asks about the project rather than asking to change it.
---

# ask-project

Talk about the project. The user asks, you answer from the project's own files, and point to the skill that would act on it. **You never change anything**: no registry, spec, config or Paper writes.

**Plugin root:** this skill's real directory, two levels up. The rules you answer against are in `references/` (nodes-and-layout, coverage-checklist, project-and-paper).
**Project:** `design/user-flow/`. If it's missing, say so and offer **init**.

## 1. Read the project (every time, before answering)
- `python3 design/user-flow/specs/_uf.py brief`: status, maps, every gap with its state, blockers and path, open and decided questions, rules, and library coverage. This is your main source.
- For "what's missing" or coverage questions: `python3 design/user-flow/specs/_uf.py coverage` (library screen families × maps; families on no map yet).
- Then only what the question needs:
  - a journey's detail: its spec, `specs/j<n>.py` (rows, nodes, arrows, notes);
  - a screen: `_uf.py find <words>` and `library.json`;
  - what a gap needs: `gaps.json`; a decision: `questions.json`;
  - the product and its promises: the repo's AGENTS.md / CLAUDE.md / README, and `config.json` → `rules`;
  - how it looks: Paper, read-only (`get_screenshot`, `get_tree_summary`), and only when the files can't answer. Pass the file id on every call.

## 2. Answer
- **Lead with the answer**, in a sentence or two. Then the detail, as a short list or a small table.
- **Cite ids** so the user can find things: gaps `N2·3`, questions `Q1·3`, screens by their library ref (`DO4`, `5.4·7`), maps `J2 row 3`, boards by name.
- **Keep facts and judgement apart.** Facts come from the files ("N1·2 waits on Q1·3"). Judgement is yours and says so ("I'd design N1·3 first: it's the only sign-in failure and it's on every way in").
- **Say what you don't know.** A board painted before its last change, a question nobody raised, a family no map covers yet.

What good answers draw on:
- **Status:** `brief` → Status. Out-of-date boards, what's exploring, what's promoted, what's waiting on whom.
- **Missing journeys and flows:** `coverage` → families on no map, grouped by area (from the master map). Name them as journeys to map, biggest or most-used first.
- **Still to design:** gaps by state. On the persona's path first, then unblocked, then the rest. Say which are blocked, and by what.
- **What to look out for:**
  - open questions that block gaps;
  - rules at risk ("never ask two things back to back" near two permission alerts);
  - screens a map shows from outside the library (their notes say so);
  - explorations confirmed but not promoted;
  - Paper's file-size limit, if boards keep growing.
- **Edge cases:** walk `references/coverage-checklist.md` against the journey the user means, read from its spec. List what's drawn, what's a gap, and what's not covered at all. Only the last group is new. Offer **audit-flow** to add those.

## 3. Close with what to do next
One to three suggestions, each naming the skill that does it: "Map the top's week (**map-journey**)", "Answer Q1·3 to unblock N1·2 (**answer-questions**)", "Add the 3 uncovered edge cases (**audit-flow**)". Don't run them. The user decides.
