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
3. If the project exists, read `config.json` and `gaps.json`. Print a status block before routing:

```
<Project> · user-flow
Master map: <artboard or "not yet">
Journeys: 1 Getting in (N designed · N to design) · 2 Collecting (…)
Flows: <job names or "none">
States: <state maps or "none">
Gaps: <todo> to design · <exploring> exploring · <explored> explored · <promoted> promoted · <later> after MVP
Questions: <open> open · <waiting> waiting on someone
Boards out of date: <boards whose spec renders a non-empty sync plan, or "none">
Next up: <the first todo gap on the persona's path, e.g. N1·2 Email sign-in>
```

## The skills

| Skill | Use when the user wants to… | Example prompts |
|---|---|---|
| **init** | set up a project: sources (Paper, Figma, codebase), persona, theme, UI kit | "set this up", "start user-flow for this app", "connect my Paper file" |
| **map-master** | see every screen in the app, grouped by area: the inventory | "map everything", "all the screens", "what screens do we have" |
| **map-journey** | map one area end to end, with every branch (a segment of the master) | "map onboarding", "journey for collecting", "journey 3: the week in the top" |
| **map-flow** | map one job to be done, start to finish, across areas | "flow for saving a TikTok and planning Saturday", "the JTBD for booking" |
| **audit-flow** | find missing screens and states in a map, and add them as gaps | "audit journey 2", "what's missing", "check this flow for edge cases" |
| **map-states** | list every state one surface can show, in priority order, and who wins | "what shows in the top when", "states of the banner", "which one wins" |
| **explore-design** | design a gap: references, 3 directions, rounds, confirm | "explore N2·3", "design the email sign-in", "iterate on B", "confirm A", "more variants" |
| **promote-design** | move a confirmed design onto the screens page for developers | "promote N2·1", "hand this to the devs", "publish the confirmed screens" |
| **answer-questions** | answer open questions and apply what each answer changes | "answer the open questions", "Q1·3: code", "what's still undecided" |
| **sync-board** | update a board on the canvas to match its spec | "sync journey 2", "refresh the maps", "the board looks out of date" |

## Routing rules
- **A gap id** (`N2·3`) or "explore / design / iterate / confirm / more variants" goes to **explore-design**.
- **"Map" plus an area or section** goes to **map-journey**. **"Map" plus a goal or job** ("to plan a night out") goes to **map-flow**. **"Everything" or "all screens"** goes to **map-master**.
- **"Audit", "missing", "edge cases", "what did we miss"** go to **audit-flow**. The map skills also run audit-flow themselves after drawing.
- **"Promote", "hand off", "publish", "to the devs"** go to **promote-design**. **Answers to Q ids, or "decide", "undecided"** go to **answer-questions**. **"Sync", "refresh", "update the board", "out of date"** go to **sync-board**.
- **"What shows when", "which wins", states of one surface** go to **map-states**.
- **Several steps in one prompt** ("map journey 3 and explore its gaps") run in order: map-journey, then audit-flow, then explore-design on the gap the user picks.
- Every skill that changes a spec or registry finishes with **sync-board** for the boards it touched. Say which boards those were.
- **Unclear request:** ask one question with 2 to 4 options drawn from the table. Don't guess between two map levels.

## What to say before handing over
One line: "Running **map-journey** for 'The week in the top' (journey 3)." Then follow that skill's instructions exactly.
