# Painting and syncing boards

Every board is a list of keyed elements. A key is stamped at the front of each top-level layer name, for example `j2:g_share · N2·1 · Share to Argo`. `boards/<board>.json` records what is on the canvas. Because of those two things, a change never needs a repaint: sync inserts, replaces and deletes only what changed.

## Render
```
python3 specs/<spec>.py
```
It prints the element count, the full-paint chunk count, the artboard size, and the sync plan: either `no committed state yet → paint in full`, or `N insert · N replace · N delete`.

## First paint (mode: full)
1. Create the artboard at the printed size, on the right page. Maps go on the maps page and explorations on the explore page (see `config.json` → `sources.paper`). If the board already exists unkeyed (painted before sync existed), delete its children first.
2. Paste every `out/<board>/full/NN.html` into the artboard with `write_html(insert-children)`, byte for byte.
   - 1 to 4 chunks: paste them yourself.
   - More than that: split them across 2 or 3 subagents using the prompt below.
3. Screenshot the whole artboard and review it. Fix problems in the spec, then re-render. The re-render now shows a sync plan.
4. Commit: `python3 specs/<spec>.py --commit <artboard id>`. Record the artboard in `config.json` → `maps`.

## Sync (mode: sync)
1. `get_children(<artboard>)`. Save the JSON result to `out/<board>/children.json`.
2. `python3 specs/<spec>.py --drift out/<board>/children.json`.
   - This adds node ids to `out/<board>/sync/plan.json` and prints drift.
   - **unkeyed:** elements someone added by hand.
   - **missing:** keyed elements someone deleted.
   - If drift shows hand edits, show them to the user before overwriting. Offer to fold the edits into the spec, or to discard them.
3. Run the ops in `plan.json`, in order:
   - `delete`: `delete_nodes([node, ...])` in one call.
   - `replace`: `write_html(mode='replace', targetNodeId=node, html=<file>)` for each.
   - `insert`: `write_html(mode='insert-children', targetNodeId=<artboard>, html=<file>)`. Several insert files can be joined into one call.
   - If `size_changed`, update the artboard's width and height with `update_styles`.
4. Screenshot the changed area, then commit (`--commit <artboard id>`).

If a replace target is missing (the warning in step 2), or more than about 60% of the elements changed, paint in full instead.

## Paste subagent prompt (use exactly this)
> You are pasting pre-generated HTML into a Paper design file. Do exactly this and nothing else.
> First load the tool: call ToolSearch with query "select:mcp__paper__write_html" (max_results 1).
> Then, for each file in this order: <absolute paths>
> 1. Read the file.
> 2. Call mcp__paper__write_html with fileId "<file id>", targetNodeId "<artboard id>", mode "insert-children", and html set to the file's contents EXACTLY, byte for byte. Do not reformat, shorten, fix or change anything.
> Do not call any other Paper tool. If a write fails, retry that same file once. If it fails again, stop and report the file and the error.
> When done, reply with one line per file: the file name and "ok" or the error.

## Moving a board
`move_nodes([{nodeId: <artboard>, parentId: 'root_node_<page id>'}])` moves a board to another page with its keys intact. Update `config.json` afterwards.
