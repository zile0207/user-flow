---
name: map-journey
description: Map one area of the app end to end as a flowchart, with the persona's path as the spine and every other way through as branches, decisions and needs-design gaps. Use when the user wants to map a journey, a segment, a section like onboarding or collecting, or asks for every scenario in one part of the app.
---

# map-journey

A journey map is one area of the app, drawn as a full flowchart:
- The persona's path runs along row 1 in the accent colour.
- Every other way through branches off it and joins back.
- Each screen that doesn't exist yet is a dashed gap card with an id.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (all of it), `references/sync.md` and `references/project-and-paper.md`. Reference specs: `templates/examples/j1.py` and `j2.py`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Scope
- Pick the journey: its name, its number (the next free `no` in `config.json` → `maps.journeys`), and the area it covers.
  - If the master map exists, take the area from it.
  - If the request is vague, offer 2 to 4 areas from the master map, or from the source chapters.
- Find the persona's path through this area in the source (story, chapters, dates). That path is row 1.

## 2. Inventory (write it down before drawing)
- Read every source screen in scope: screenshot plus tree summary for each chapter.
- List the nodes (screens, decisions, background work, outside steps, entries, exits) and the edges, each with what causes it.
- Run `references/coverage-checklist.md` against the list. Anything missing becomes a gap:
  - `gid = P.add_gap(no, title, need, where)`
  - An existing gap from the registry is reused with `P.g(gid)`, never duplicated.
- Show the user the list in short form: rows, screens per row, new gaps. Ask "go ahead?" before drawing, unless they said to go straight through.

## 3. Spec
- Export the screens you need: `img/<node id>.png`.
- Write `specs/j<no>.py`, following the examples:
  - `from _uf import P`, `from uf.jmap import Map, row_y`, `m = Map(<no>, P)`
  - Rows via `row_y(n)`, nodes via `m.seq(...)`, or explicit x following the spacing rules.
  - Gaps are always `m.gap(id, x, y, **P.g(gid))`.
  - Arrows are labelled with what caused them. Only the persona's path uses `'coral'`.
  - `m.render(P, 'j<no>', W, title, right, story, rows, P.panel('J<no>', x, y, w))`.
  - Questions the inventory raised go in with `P.add_question('J<no>', text)`. The panel renders from them.
  - Copy in notes and needs follows `config.json` → `rules`.
- Run it. Fix any failed check in the spec.

## 4. Paste and review
- Create the artboard `<no> · <Name> · journey map` right of the existing journeys. Paint it in full (`references/sync.md`), then `--commit`.
- Screenshot it. Look for overlapping labels, crowded lanes, and arrows that cross where they could go round. Fix them in the spec, re-render, then **sync-board**.
- Record the artboard in `config.json` → `maps.journeys`. If the master map exists, add the new gaps to their area in `specs/master.py`.

## 5. Report
- Rows, and the counts: designed, to design, decisions.
- The new gaps with their ids.
- The open questions.
- Next: **audit-flow** (if you skipped the checklist), or **explore-design** on the most important gap.
