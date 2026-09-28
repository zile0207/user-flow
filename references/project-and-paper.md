# Project folder and working in Paper

## The project folder (made by init)

```
<app repo>/design/user-flow/
  config.json         shared settings (committed)
  config.local.json   this machine: {"plugin_root": "..."} (gitignored)
  gaps.json           gap registry: the only place gap ids, text and state live (committed)
  questions.json      open questions and decisions per map, rendered into each map's panel (committed)
  boards/<board>.json what is painted on each Paper board, for sync (committed, written by --commit)
  ui_kit.py           the app's screen parts for explorations (committed)
  specs/_uf.py        bootstrap: every spec starts with `from _uf import P`
  specs/master.py     master map
  specs/j<N>.py       journey maps
  specs/f<N>.py       flow maps (JTBD)
  specs/states_<slug>.py  state maps
  specs/explore_<id>.py   exploration boards, id with - for · (explore_n2_1.py)
  img/                screen PNGs named after their source id (gitignored, re-exportable)
  refs/               reference images (gitignored)
  out/<name>/NN.html  rendered chunks (gitignored)
```

`config.json`:
```json
{
  "project": "Argo",
  "plugin_version": "0.3.0",
  "device_label": "Mobile · iPhone",
  "theme": {"accent": "#E05254", "font": "Switzer", "device": [390, 844]},
  "sources": {
    "paper": {"file_id": "...",
              "screens_page": "p-2-0", "screens_page_name": "User Flow",
              "more_screens_pages": [{"id": "p-1-0", "name": "Confirmed Screens From Exploration", "use": "decided variants, read only"}],
              "maps_page": "p-3-0", "maps_page_name": "User Journey",
              "explore_page": "p-4-0", "explore_page_name": "Exploration",
              "legacy_file_ids": ["..."]},
    "figma": {"file_url": "...", "screens_page": "..."} | null,
    "codebase": {"router": "expo-router", "routes": "app", "components": "src/components"} | null
  },
  "persona": {"name": "Jamie", "summary": "...", "story_artboard": "..."},
  "screen_ids": "how screens are named, and the fallback (see Screen ids below)",
  "rules": {"copy": ["..."], "product": ["..."], "files": "where each kind of board lives, and what is off limits"},
  "promote_prefix": "X",
  "maps": {"master": {"spec": "specs/master.py", "artboard": "..."} | null,
           "journeys": [{"no": 1, "name": "Getting in", "spec": "specs/j1.py", "artboard": "..."}],
           "flows": [{"no": 1, "job": "When I…, I want to…, so I can…", "spec": "specs/f1.py", "artboard": "..."}],
           "states": [{"element": "The top", "spec": "specs/states_top.py", "artboard": "..."}],
           "explorations": [{"gap": "N2·1", "spec": "...", "artboard": "...", "page": "p-4-0", "state": "confirmed", "chosen": "A"}],
           "promoted": [{"journey": 2, "spec": "specs/promoted_j2.py", "artboard": "...", "page": "p-2-0"}]}
}
```
- `legacy_file_ids`: files no skill may write to. Check every Paper write's file id against this list.
- `more_screens_pages`: other pages with finished screens. map-master reads them too; promote-design never writes there unless the user says so.

## The registries: gaps and questions
`gaps.json` entries: `{"id", "map", "title", "need", "where", "state", "on_path"?, "round"?, "chosen"?, "img"?, "board"?, "screen_ids"?, "chapter"?}`.
`questions.json` entries: `{"id", "map", "text", "about", "state": "open" | "waiting" | "decided", "decision"?, "owner"?, "date"?, "blocks"?}`.

Change them with the project command line, **once, from the shell, never inside a spec** (a spec runs on every render):
```
python3 design/user-flow/specs/_uf.py gaps [--state todo] [--map J1]
python3 design/user-flow/specs/_uf.py add-gap 2 "Reading timed out" "Say Argo gave up; keep what it found." "row 3"
python3 design/user-flow/specs/_uf.py set-gap N2·3 state=exploring round=1 board=2A9X-0
python3 design/user-flow/specs/_uf.py questions [--state open]
python3 design/user-flow/specs/_uf.py add-question J1 "Code or password?" --blocks N1·2
python3 design/user-flow/specs/_uf.py answer Q1·3 "A 6-digit code, no password." --date "Tue 29 Sep"
python3 design/user-flow/specs/_uf.py answer Q2·2 --owner "the developers"      # asked, no answer yet
python3 design/user-flow/specs/_uf.py add-rule product "Sharing is after MVP."
python3 design/user-flow/specs/_uf.py status
```
- `add-gap` and `add-question` are safe to repeat: the same title (or text) on the same map returns the existing id.
- Ids are never renumbered or reused.
- `on_path` is set by the journey render: a gap touched by the persona's (accent) arrow is on the path. The status "Next up" uses it.
- A question `blocks` gaps (or names a gap id in its text): explore-design asks for the answer first.
- In Python the same calls are `P.add_gap`, `P.set_gap`, `P.add_question`, `P.answer`, `P.add_rule`, `P.blocking`, with `from _uf import P` (run from `specs/`).

## Screen ids
A screen keeps the id its source gives it: the Paper page's chapter·step (`E7·5`), a Figma frame name, or a route.
When the source has no usable step number (steps unnumbered, restarting in a second row, or old names), fall back in this order and write the rule into `config.json` → `screen_ids`:
1. chapter + reading order on the artboard: left to right, then top to bottom (`J3·1`, `J3·2`…);
2. a second row that restarts its numbers gets a letter (`A5·b2`);
3. a frame named with an older scheme keeps that name as `ref`, with the chapter in front (`B1 · DO9`).

## Duplicates
The same screen shown twice in a story counts once on the master map. It's a duplicate when the frame name **and** the step label match, or when two exports are pixel-identical after cropping the status bar. Keep screens that differ in state (empty, error, loading, a different sheet stop) even if they look alike.
## Rendering and painting
- Run `python3 specs/<spec>.py`. A failed check (overlap, a decision with one exit, a missing gap id) is a bug in the spec: fix the spec. Warnings (labels overlapping, a row with no label) are layout problems a person would see: fix them too.
- `sync.md` covers painting a new board in full, syncing an existing one, checking for hand edits, and the paste subagent prompt.
- The rules in `config.json` → `rules` apply to everything an agent writes: map notes, gap needs, and the copy in explorations.

## Exporting screens
- `export({nodes: {<node id>: [{format: 'png', scale: '1x'}]}})` writes `~/Downloads/<layer name>.png` and returns each `filePath`. Move each file into `img/<node id without -0>.png` straight after the batch.
- **Batches of at most 12 nodes.** Bigger batches can return `[]` and write only some files.
- **Never two nodes with the same layer name in one batch:** they write to the same file. Split them across batches.
- Paper turns `/ : ?` in names into `_`. Use the returned `filePath`, don't rebuild the name.
- After each batch, count the files you moved. Re-export anything missing. Only delete files you created.
- Thumbnails use `paper-asset://<absolute path>`. Paper uploads the image when you paste.

## Reading sources
- **Paper:** get_basic_info for the screens page, get_tree_summary for each artboard, and a screenshot to understand it. Use get_jsx or get_computed_styles for exact values (the UI kit), never screenshots.
- **Figma:** the Figma MCP (`get_metadata`, `get_design_context`, `get_screenshot`). Load the figma-use skill first where required.
- **Codebase:** the router folder gives the list of screens (with Expo Router, file path = route). Read each screen file for its states: loading, empty, error. Screens that exist only in code get `ref` = route.
