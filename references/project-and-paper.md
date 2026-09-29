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
  library.json        index of the library page: every confirmed screen, with its node id (committed)
  refs/               reference images from other apps, for explorations only (gitignored)
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
              "library_page": "p-1-0", "library_page_name": "Confirmed Screens From Exploration",
              "promote_page": "p-1-0",
              "master_page": "p-5-0", "master_page_name": "Master Map",
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
- `library_page`: the page that holds every confirmed screen of the app, however messy (see The library). `screens_page` is the curated story, if there is one.
- `master_page` (optional): a page of its own for the master map; otherwise it goes first on the maps page.
- `promote_page`: where promote-design puts confirmed explorations. Defaults to the library page, else the screens page.

## The registries: gaps and questions
`gaps.json` entries: `{"id", "map", "title", "need", "where", "state", "on_path"?, "round"?, "chosen"?, "node"?, "ref"?, "board"?, "screen_ids"?, "chapter"?}`. `node` is the Paper frame the map shows once the gap is `found`, `explored` or `promoted`.
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
The same screen shown twice in a story counts once on the master map. It's a duplicate when the frame name **and** the step label match, or when two frames have the same tree summary and screenshot. Keep screens that differ in state (empty, error, loading, a different sheet stop) even if they look alike.
## Rendering and painting
- Run `python3 specs/<spec>.py`. A failed check (overlap, a decision with one exit, a missing gap id) is a bug in the spec: fix the spec. Warnings (labels overlapping, a row with no label) are layout problems a person would see: fix them too.
- `sync.md` covers painting a new board in full, syncing an existing one, checking for hand edits, and the paste subagent prompt.
- The rules in `config.json` → `rules` apply to everything an agent writes: map notes, gap needs, and the copy in explorations.

## Screens on boards: real frames, never images
Every screen on a map, the master map or a state map is a **live copy of the real Paper frame at its real size** (390×844 on iPhone), made by the renderer as `<x-paper-clone node-id="…">` (`uf.base.screen`). No zoom, no shrinking: the copy's layers are exactly as big as they look, so selecting it on the canvas selects what you see.
- To make room, boards are drawn larger than their specs: specs stay in map units (a card is 200 wide), and `Board(scale=…)` scales every position, size, font and arrow so a card's screen box comes out at the device width. A journey map is drawn about 2.2× its spec; the master and state maps about 3.1×.
- Specs name frames by **node id** (`node='PY1-0'`), never by image. Don't export PNGs of screens, and don't put `<img>` screenshots of the app on any board. The only images allowed are an exploration's references from other apps.
- Take the node from the **library page** where the screen exists there. Use another page's frame only when the library doesn't have it, and say so in the card's note.
- A copy doesn't follow later edits to its source. When a library screen changes, run `_uf.py stale <board> <node id>` (or `all`) and sync: those copies are replaced with fresh ones.
- Pasting copies returns very large responses (every copied layer is listed). Chunks hold at most 6 copies; always paste chunks with copies through the paste subagent.

## The library
The library page holds every confirmed screen, however it's organised. Journeys put these screens in context, so **before anything becomes a needs-design gap, look for it in the library.**
- Index it once, and again when the page changes: `get_tree_summary(root_node_<library page>, depth 1)` → save to `out/library_tree.txt` → `python3 design/user-flow/specs/_uf.py library out/library_tree.txt`. Frames as wide as the device are screens; wider or short frames are headers and bands.
- `_uf.py find <words>` or `_uf.py find --gap N2·3` lists candidate screens by name. Confirm each with `get_screenshot` before using it.
- `_uf.py unplaced <board> <group,group>` lists library screens in those groups (the first part of a frame name, like `5.4`, `DO`, `MON`) that the board doesn't show yet.
- A gap the library already covers becomes `found`: `_uf.py set-gap N1·5 state=found node=PY1-0 ref=DO4`. Maps then show that frame, labelled "DO4 · was N1·5".

## Reading sources
- **Paper:** get_basic_info for the screens page, get_tree_summary for each artboard, and a screenshot to understand it. Use get_jsx or get_computed_styles for exact values (the UI kit), never screenshots.
- **Figma:** the Figma MCP (`get_metadata`, `get_design_context`, `get_screenshot`). Load the figma-use skill first where required.
- **Codebase:** the router folder gives the list of screens (with Expo Router, file path = route). Read each screen file for its states: loading, empty, error. Screens that exist only in code get `ref` = route.
