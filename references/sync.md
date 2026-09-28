# Painting and syncing boards

Every board is a list of keyed elements. A key is stamped at the front of each top-level layer name, for example `j2:g_share · N2·1 · Share to Argo`. `boards/<board>.json` records what is on the canvas. Because of those two things, a change never needs a repaint: sync deletes, renames, replaces, moves and inserts only what changed.

Pass `fileId` on every Paper call. Tools without it act on whatever file the person is looking at.

## Render
```
python3 specs/<spec>.py
```
It prints the element count, the full-paint chunk count, the artboard size, any layout warnings, and the sync plan: either `no committed state yet → paint in full`, or `N insert · N replace · N move · N rename · N delete`. Fix warnings (labels overlapping, a row without a label) in the spec before painting.

## First paint (mode: full)
1. Create the artboard at the printed size, on the right page. Maps go on the maps page and explorations on the explore page (see `config.json` → `sources.paper`). `create_artboard` ignores left and top: place it afterwards with `update_styles` (left, top), 80px or more right of the last board. If the board already exists unkeyed (painted before sync existed), delete its children first.
2. Paste every `out/<board>/full/NN.html` into the artboard with `write_html(insert-children)`, byte for byte, in order.
   - 1 or 2 chunks: paste them yourself.
   - More: hand them to **one** paste subagent at a time, with the prompt below (up to 6 chunks each). Never run two paste agents on the same artboard at once: the layer order would interleave.
3. **Commit straight away:** `python3 specs/<spec>.py --commit <artboard id>`. The board now matches the spec, so from here on every change is a sync.
4. Record the artboard in `config.json` → `maps`.
5. Review: screenshot the whole board, then each row at scale 1 (a whole-board screenshot is too small to read 12px labels). Fix problems in the spec, re-render, and sync.

## Sync (mode: sync)
1. **Read the board:** `get_tree_summary(<artboard>, depth 1)`. Save it to `out/<board>/tree.txt`: either the whole result, or one line per child, `<node id> <layer name>`. Only the part of the name before ` · ` matters.
   - Don't use `get_children` for this: it stops at 100 children, and `--drift` refuses a cut list.
2. **Drift:** `python3 specs/<spec>.py --drift out/<board>/tree.txt`. This puts node ids into `out/<board>/sync/plan.json` and prints:
   - **unkeyed:** elements someone added by hand, with their node ids.
   - **missing:** keyed elements someone deleted.
   - Drift can't see edits *inside* an element (changed text, colour or position). If the board has been open to other people, ask whether they edited it by hand.
   - If drift shows hand edits, show them to the user before changing anything. They choose:
     - **keep:** fold the edit into the spec (a new node, a changed note), re-render, and run drift again;
     - **discard:** delete the unkeyed nodes (`delete_nodes`) along with the plan's deletes.
3. **Run the ops** in `plan.json`, in this order, batching where the tool allows:
   - `delete`: one `delete_nodes` call with every `node`.
   - `rename`: one `rename_nodes` call: `{nodeId: node, name: name}` for each. (The element didn't change, only its key.)
   - `replace`: `write_html(mode='replace', targetNodeId=node, html=<file>)`, one call each. Note the new node id it returns. `write_html(replace)` keeps the old node's position, so every replace also needs its `left`/`top` set (next step).
   - `move` and replaced positions: one `update_styles` call, one entry per node: `{nodeIds: [node], styles: {left: '<left>px', top: '<top>px'}}`. Use the new node ids for replaced elements.
   - `insert`: each `ins_NN.html` file with `write_html(mode='insert-children', targetNodeId=<artboard>)`.
   - If `size_changed`, set the artboard's width and height with `update_styles`.
   - More than about 8 replaces: hand them to one subagent with the replace prompt below.
4. **Check:** screenshot the areas that changed, then the whole board.
5. **Commit:** `python3 specs/<spec>.py --commit <artboard id>`.

When the plan is `0 · 0 · 0 · 0 · 0`, there is nothing to paint. Still run drift if the board may have been edited by hand, and say so either way. No commit is needed.

If a target is missing (the warning in step 2), or more than about 70% of the elements are replaced or inserted, paint in full instead: delete the artboard's children, paste `full/`, commit.

## Paste subagent prompt (use exactly this)
> You are pasting pre-generated HTML into a Paper design file. Do exactly this and nothing else.
> First load the tool: call ToolSearch with query "select:mcp__paper__write_html" (max_results 1).
> Then, for each file in this order: <absolute paths>
> 1. Read the file.
> 2. Call mcp__paper__write_html with fileId "<file id>", targetNodeId "<artboard id>", mode "insert-children", and html set to the file's contents EXACTLY, byte for byte. Do not reformat, shorten, fix or change anything.
> Do not call any other Paper tool. If a write fails, retry that same file once. If it fails again, stop and report the file and the error.
> When done, reply with one line per file: the file name and "ok" or the error.

## Replace subagent prompt (use exactly this)
> You are replacing elements in a Paper design file with pre-generated HTML. Do exactly this and nothing else.
> First load the tools: call ToolSearch with query "select:mcp__paper__write_html,mcp__paper__update_styles" (max_results 2).
> For each line below, in order: `<node id> <absolute file path> <left> <top>`
> 1. Read the file.
> 2. Call mcp__paper__write_html with fileId "<file id>", targetNodeId set to the node id, mode "replace", and html set to the file's contents EXACTLY, byte for byte. Note the id of the new top-level node it returns.
> After all replaces, call mcp__paper__update_styles once, with fileId "<file id>" and one update per new node: styles {"left": "<left>px", "top": "<top>px"}.
> Do not call any other Paper tool. If a call fails, retry it once, then stop and report.
> Reply with one line per element: the old node id, the new node id, and "ok" or the error.

## Moving a board
`move_nodes([{nodeId: <artboard>, parentId: 'root_node_<page id>'}])` moves a board to another page with its keys intact. Update `config.json` afterwards.
