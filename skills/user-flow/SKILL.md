---
name: user-flow
description: The index for the user-flow plugin. Describe what you want in plain words (map the whole app, a journey, one job or one surface's states; audit a map; explore, promote or sync a design; answer open questions) and it routes to the right skill.
disable-model-invocation: true
---

# user-flow

You are the router for the user-flow plugin. The user types `/user-flow`, usually followed by what they want. Work out which skill fits, confirm it in one line, then run that skill with the user's words passed on.

## Setup check (always first)
1. **Plugin root:** resolve this skill's real directory (follow symlinks), then go two levels up. Its `references/` and `lib/` are the shared rules and code.
2. **Project:** look for `design/user-flow/config.json` in the current repo.
   - If it's missing and the request is anything but init, say so and run **init** first.
3. If the project exists, run `python3 design/user-flow/specs/_uf.py status` and print its output as it is. Don't work the numbers out yourself: the script renders every spec, so the counts, the out-of-date boards and "Next up" are the same whichever agent runs it. It looks like:

```
Argo · user-flow
Master map: not yet
Journeys: 1 Getting in (14 designed · 11 to design) · 2 Collecting (31 designed · 9 to design)
Flows: none
States: none
Gaps: 20 to design · 0 exploring · 1 explored · 0 promoted · 1 after MVP
Questions: 7 open · 1 waiting on someone
Boards out of date: none
Next up: N1·1 Apple sign-in (no open gap on Jamie's path; first open gap)
```
   If the script fails (an older project without the command line), copy `templates/project/specs/_uf.py` over the project's copy first (it only adds the command line), and commit it with the project's next commit.
4. With no request after `/user-flow`, print the status, then offer 3 or 4 next steps drawn from it (the next-up gap, open questions, out-of-date boards).

## The skills

| Skill | Use when the user wants to… | Example prompts |
|---|---|---|
| **init** | set up a project: sources (Paper, Figma, codebase), persona, theme, UI kit | "set this up", "start user-flow for this app", "connect my Paper file" |
| **map-master** | see every screen in the app, grouped by area: the inventory | "map everything", "all the screens", "what screens do we have" |
| **map-journey** | map one area end to end, with every branch (a segment of the master), or update and re-lay out one | "map onboarding", "journey for collecting", "journey 3: the week in the top", "redo journey 1, the arrows cross" |
| **map-flow** | map one job to be done, start to finish, across areas | "flow for saving a TikTok and planning Saturday", "the JTBD for booking" |
| **audit-flow** | find missing screens and states in a map, and add them as gaps | "audit journey 2", "what's missing", "add a screen for when the link is private" |
| **map-states** | list every state one surface can show, in priority order, and who wins | "what shows in the top when", "states of the banner", "which one wins" |
| **explore-design** | design a gap: references, 3 directions, rounds, confirm | "explore N2·3", "design the email sign-in", "iterate on B", "confirm A", "more variants" |
| **promote-design** | move a confirmed design onto the screens page for developers | "promote N2·1", "hand this to the devs", "publish the confirmed screens" |
| **answer-questions** | answer open questions and apply what each answer changes | "answer the open questions", "Q1·3: code", "what's still undecided" |
| **sync-board** | update a board on the canvas to match its spec | "sync journey 2", "refresh the maps", "the board looks out of date" |

## Routing rules
Check these in order. The first that matches wins.
0. **Several steps in one prompt** ("map everything then explore the first gap"): split it into steps, route each step with the rules below, and run them in order. After each map step, run its audit. "The first gap" means the status line's Next up; otherwise ask which gap.
1. **Set up:** "set up", "init", "connect my Paper/Figma file", another app or repo → **init** (in that repo).
2. **Hand-off:** "promote", "hand off", "publish", "to the devs", "developers can build" → **promote-design**, even when the prompt names a gap id.
3. **Answers and decisions:** a Q id with an answer ("Q1·3: code"), "decide", "undecided", "open questions" → **answer-questions**.
4. **Sync:** "sync", "refresh", "update the board", "out of date", "repaint" → **sync-board**. If no board is named, sync every board the status lists as out of date; if none are, say so.
5. **States of one surface:** "what shows when", "which wins", "states of the …" → **map-states**.
6. **Audit:** "audit", "missing", "edge cases", "what did we miss" → **audit-flow**.
7. **Add one screen or state to a map:** "add a screen for …", "we need a state for …" → **audit-flow** with that one finding: check the map first (it may already be drawn, or already be a gap), then add it as a gap.
8. **Design work:** a gap id (`N2·3`), or "explore", "design the …", "iterate on", "more variants", "mix", "confirm X" → **explore-design**. A gap named by title ("the email sign-in") is fine: explore-design matches it.
9. **Maps:**
   - "everything", "all screens", "inventory" → **map-master**.
   - "map" + an area or section ("onboarding", "collecting") → **map-journey**. If a journey already covers that area, it updates that journey instead of making a new one.
   - "map" + a goal or job ("to plan a Saturday", "how Jamie plans a Saturday") → **map-flow**.
   - "redo", "re-lay out", "the arrows cross" on an existing map → **map-journey** (or map-flow) in update mode, then **sync-board**.
- Every skill that changes a spec or registry finishes with **sync-board** for the boards it touched. Say which boards those were.
- **Unclear request:** ask one question with 2 to 4 options drawn from the table. Don't guess between two map levels.

## What to say before handing over
One line: "Running **map-journey** for 'The week in the top' (journey 3)." Then follow that skill's instructions exactly.
