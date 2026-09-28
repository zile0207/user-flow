# Project folder and working in Paper

## The project folder (made by init)

```
<app repo>/design/user-flow/
  config.json         shared settings (committed)
  config.local.json   this machine: {"plugin_root": "..."} (gitignored)
  gaps.json           gap registry: the only place gap ids, text and state live (committed)
  ui_kit.py           the app's screen parts for explorations (committed)
  specs/_uf.py        bootstrap: every spec starts with `from _uf import P`
  specs/master.py     master map
  specs/j<N>.py       journey maps
  specs/f<N>.py       flow maps (JTBD)
  specs/explore_<id>.py   exploration boards, id with - for · (explore_n2_1.py)
  img/                screen PNGs named after their source id (gitignored, re-exportable)
  refs/               reference images (gitignored)
  out/<name>/NN.html  rendered chunks (gitignored)
```

`config.json`:
```json
{
  "project": "Argo",
  "theme": {"accent": "#E05254", "font": "Switzer", "device": [390, 844]},
  "sources": {
    "paper": {"file_id": "...", "screens_page": "p-2-0", "maps_page": "p-3-0"},
    "figma": {"file_url": "...", "screens_page": "..."} | null,
    "codebase": {"router": "expo-router", "routes": "app", "components": "src/components"} | null
  },
  "persona": {"name": "Jamie", "summary": "...", "story_artboard": "..."},
  "maps": {"master": {"spec": "specs/master.py", "artboard": "..."} | null,
           "journeys": [{"no": 1, "name": "Getting in", "spec": "specs/j1.py", "artboard": "..."}],
           "flows": [{"no": 1, "job": "...", "spec": "specs/f1.py", "artboard": "..."}],
           "explorations": [{"gap": "N2·1", "spec": "...", "artboard": "...", "state": "confirmed", "chosen": "A"}]}
}
```

`gaps.json` entries: `{"id", "map", "title", "need", "where", "state", "round"?, "chosen"?, "img"?, "board"?}`. Use `P.add_gap`, `P.set_gap`, `P.next_gap_id` and `P.g`. Never renumber.

## Rendering
- Run `python3 specs/<spec>.py` from the project. It prints the artboard size and counts, and writes `out/<name>/NN.html`.
- A failed check (overlap, a decision with one exit, a missing gap id) is a bug in the spec. Fix the spec.

## Pasting into Paper
1. Load the Paper MCP guide once per session: `get_guide('paper-mcp-instructions')`.
2. Create the artboard on the maps page at the printed size, named `<N> · <Name> · journey map`, `<N> · <Job> · flow`, `Master map`, or `Explore · <id> · <title>`. Put it to the right of the existing boards; the order is master, journeys, flows, explorations.
3. Paste each chunk with `write_html(insert-children, targetNodeId=<artboard>)`, byte for byte. For big boards, split the chunks across 2 or 3 subagents running in parallel. Tell each one: load `mcp__paper__write_html` with ToolSearch, then paste only the listed files, and do nothing else.
4. Screenshot the whole artboard. Fix anything wrong in the spec and re-render. Don't patch the canvas by hand, except for the documented targeted swaps (the confirm swaps).
5. Record the artboard id in `config.json`, then call `finish_working_on_nodes`.

## Exporting screens
- `export({nodeId: [{format: 'png', scale: '1x'}]})` writes to `~/Downloads/<layer name>.png`. Move the file into `img/<node id without -0>.png`.
- A batch export can report an empty result and still write the files. Check `~/Downloads`, and only delete files you created.
- Thumbnails use `paper-asset://<absolute path>`. Paper uploads the image when you paste.

## Reading sources
- **Paper:** get_basic_info for the screens page, get_tree_summary for each artboard, and a screenshot to understand it. Use get_jsx or get_computed_styles for exact values (the UI kit), never screenshots.
- **Figma:** the Figma MCP (`get_metadata`, `get_design_context`, `get_screenshot`). Load the figma-use skill first where required.
- **Codebase:** the router folder gives the list of screens (with Expo Router, file path = route). Read each screen file for its states: loading, empty, error. Screens that exist only in code get `ref` = route.
