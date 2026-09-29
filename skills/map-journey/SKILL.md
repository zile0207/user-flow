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
- **Library in another file** (`sources.paper.library_file_id` differs from `file_id`): the maps file keeps one real copy of each screen on its **Frames page** (`sources.paper.frames_page`), typed once; cards are live copies of those, so boards stay cheap to paint and sync. The order, fast:
  1. Render. It lists the screens not on the Frames page yet.
  2. `_uf.py frames-local j<no>`. If it lists frames to fetch: `get_jsx(fileId = library file, nodeId, format "inline-styles")` for each (one call at a time; a subagent can do them all if the user allows subagents), then `_uf.py frames-from-transcript <session .jsonl>` (in Claude Code: the newest .jsonl in `~/.claude/projects/<this repo>/`, or the subagent's), no retyping; otherwise `_uf.py frames-save`. Run `frames-local` again.
  3. Make the listed copies. Ask the user whether to use subagents: if yes, split the list across at most 3 paste subagents at once (always `model: "sonnet"`, Sonnet 5.5, low effort; never haiku), each doing create_artboard + write_html per line; if no, make them yourself, one call at a time. Then one update_styles for their positions; then `_uf.py frames-local-commit <Frames page tree>` (only the `copy:` lines are needed).
  4. Render again: no markers left. Paint the board (`sync.md` → First paint).
- **Tokens:** if the project has a token file (`sources.paper.tokens`), run **bind-tokens** on the board's library frames before its first paint (`_uf.py bind-status j<no>` lists the unbound ones), so the copies arrive tagged.
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
