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
  - **If a journey already covers this area** (or the prompt says "redo", "re-lay out", "the arrows cross"): don't make a new one. Work in **update mode**: same number, same spec, same gap ids. Edit `specs/j<no>.py`, render, and **sync-board**. Skip to step 4.
  - If the master map exists, take the area from it.
  - If the request is vague, offer 2 to 4 areas from the master map, or from the source chapters.
- Find the persona's path through this area in the source (story, chapters, dates). That path is row 1.

## 2. Inventory (write it down before drawing)
- **Start from the screen index:** `_uf.py screens --area "<area>"` (or `--group MON`, `--find <words>`) says what every library frame is (its stop, whether it's a full screen or top-only, where it's used) before you fetch or screenshot anything. Screenshot only the frames you're choosing between.
- Read every source screen in scope: the story chapters on the screens page for the persona's path, and **the library** for every screen of this area (`_uf.py find`, `_uf.py unplaced`, screenshots). Record the library groups this journey covers in `config.json` → the journey's `library_groups`.
- List the nodes (screens, decisions, background work, outside steps, entries, exits) and the edges, each with what causes it.
- Run `references/coverage-checklist.md` against the list. Anything missing is searched in the library first (`_uf.py find <words>`); only what the library doesn't have becomes a gap. An existing gap from the registry (`_uf.py gaps`) is reused, never duplicated.
- Show the user the list in short form: rows, screens per row, new gaps, open questions. Ask "go ahead?" before drawing, unless they said to go straight through.
- After the go-ahead, add the new gaps and questions **once, from the shell** (never inside the spec, which runs on every render):
  - `python3 design/user-flow/specs/_uf.py add-gap <no> "<title>" "<need>" "<where>"` prints the new id.
  - `python3 design/user-flow/specs/_uf.py add-question J<no> "<text>"`, with `--blocks <gap ids>` when a gap can't be designed until it's answered.

## 3. Spec
- Cards name the real frames by node id (`node='PY1-0'`), taken from the library where the screen exists there. Never export or show images of screens.
- **Top-only frames** (the index says "top only": the top's states, whose sheet is empty) need a sheet: `m.card(..., sheet='<node>')` names the library frame whose sheet the persona is looking at in that moment (the tab from the story: Explore, Links, Boards, Plans or Profile). The card shows the top over that real sheet.
- **Library in another file** (`sources.paper.library_file_id` differs from `file_id`): cards are copies of the frames' real layers. Render once: it lists the frames to fetch (`_uf.py frames j<no>`). Fetch each with `get_jsx(fileId = library file, nodeId, format "inline-styles")`, then store them: in Claude Code `_uf.py frames-from-transcript <your session's .jsonl>` (the newest file in `~/.claude/projects/<this repo>/`), no retyping; otherwise `_uf.py frames-save`. Render again: no markers left.
- Write `specs/j<no>.py`, following the examples:
  - `from _uf import P`, `from uf.jmap import Map, row_y`, `m = Map(<no>, P)`
  - Rows via `row_y(n)`, nodes via `m.seq(...)`, or explicit x following the spacing rules.
  - Gaps are always `m.gap(id, x, y, **P.g(gid))`.
  - Arrows are labelled with what caused them. Only the persona's path uses `'coral'`.
  - `m.render(P, 'j<no>', W, title, right, story, rows, P.panel('J<no>', x, y, w))`.
  - Copy in notes and needs follows `config.json` → `rules`.
- Run it. Fix any failed check and any warning (labels overlapping, a row with no label) in the spec.

## 4. Paste and review
- Create the artboard `<no> · <Name> · journey map` right of the existing journeys. Paint it in full (`references/sync.md`), then `--commit`.
- Screenshot the whole board, then each row at scale 1 (the whole board is too small to read labels). Look for overlapping labels, crowded lanes, and arrows that cross where they could go round. Fix them in the spec, re-render, then **sync-board**.
- Record the artboard in `config.json` → `maps.journeys`. If the master map exists, add the new gaps to their area in `specs/master.py`.

## 5. Report
- Rows, and the counts: designed, to design, decisions.
- The new gaps with their ids.
- The open questions.
- Next: **audit-flow** (if you skipped the checklist), or **explore-design** on the most important gap.
