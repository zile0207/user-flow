# Painting and syncing boards

Every board is a list of keyed elements. A key is stamped at the front of each top-level layer name, for example `j2:g_share · N2·1 · Share to Argo`. `boards/<board>.json` records what is on the canvas. Because of those two things, a change never needs a repaint: sync deletes, renames, replaces, moves and inserts only what changed.

Pass `fileId` on every Paper call. Tools without it act on whatever file the person is looking at.

## Render
```
python3 specs/<spec>.py
```
It prints the element count, the full-paint chunk count, the artboard size, any layout warnings, and the sync plan: either `no committed state yet → paint in full`, or `N insert · N replace · N move · N rename · N delete`. Fix warnings (labels overlapping, a row without a label) in the spec before painting.

## Placed screens (library in another file, `sources.paper.screens: "placed"`)
Paper can't copy a frame between files through the MCP, and retyping a screen as HTML is slow (15–60 KB each). So on these boards the agent never pastes screens. The board paints with empty, named slots (`slot · 3.1 · Profile tab`); the person copies the frames over in the Paper app, which takes seconds; the agent moves each one into its slot.
1. **Tag first:** the frames must be bound to tokens before they are staged (**bind-tokens**), so the copies carry the tags.
2. **Stage:** `_uf.py stage <board>` lists one frame per empty slot and prints one `duplicate_nodes` call that puts copies on the staging page of the library file (`sources.paper.staging_page`). Run it, then `_uf.py stage-commit <board> <the new ids, in order>`: it prints a `rename_nodes` call (each copy named after its slot) and an `update_styles` grid. Run both.
3. **Hand over:** tell the person exactly what `stage-commit` printed: select every frame on the staging page, copy, and paste them anywhere on the board's page with nothing selected. Paint the board (below) while they do it.
4. **Place,** once they say the frames are there:
   - `get_tree_summary(root_node_<board page>, depth 1)`: the pasted frames, by name.
   - `get_tree_summary(<artboard>, depth 2)`: the slots, inside the cards.
   - `_uf.py place <board> <page tree> <board tree>` prints one `move_nodes` call (each frame into its slot) and one `update_styles` (pinned at left/top 0). It lists any slot whose frame isn't on the page yet. Run both calls, then screenshot two cards at scale 1.
5. **Clean up:** `_uf.py stage-clear <board>` prints the `delete_nodes` call for the copies left on the staging page.

A placed screen stays through every sync: when a card is replaced, `ops` moves its screen out first and back into the new card's slot after. A card that now shows a different frame, or whose frame changed on the library (`_uf.py stale <board> <node>`), gets an empty slot again: stage and place it the same way.

## First paint (mode: full)
1. Create the artboard at the printed size, on the right page. Maps go on the maps page and explorations on the explore page (see `config.json` → `sources.paper`). `create_artboard` ignores left and top: place it afterwards with `update_styles` (left, top), 80px or more right of the last board. If the board already exists unkeyed (painted before sync existed), delete its children first.
2. Paste the chunks in `out/<board>/full/` into the artboard with `write_html(insert-children)`, byte for byte, following `full/paint.json`:
   - **Placed boards** have no screen HTML, so every chunk is small: paste them yourself, in order. Skip the rest of this step.
   - **Ask the user first** whether to use subagents for this paint. Subagents are never assumed.
   - `parallel`: the chunks that hold screens. They never overlap each other. With subagents allowed, split them across **at most 3 paste subagents at once**, up to 6 chunks each, with the prompt below (always `model: "sonnet"`, Sonnet 5.5, at low effort; never haiku: pasting is verbatim copying, so it needs no more). Without subagents, paste them yourself, one call at a time.
   - `serial`: arrows, labels, panels. After every screen chunk is on the canvas, paste these in order (one subagent, or yourself), so they sit on top of the screens.
   - Screenshot only after the pastes are done (a screenshot sent alongside shows the board before the paste).
3. **Commit straight away:** `python3 specs/<spec>.py --commit <artboard id>`. The board now matches the spec, so from here on every change is a sync. (Placed boards: then place the screens, above.)
4. Record the artboard in `config.json` → `maps`.
5. Review: screenshot the whole board, then each row at scale 1 (a whole-board screenshot is too small to read 12px labels). Fix problems in the spec, re-render, and sync.

## Sync (mode: sync)
1. **Read the board:** `get_tree_summary(<artboard>, depth 1)`. Save it to `out/<board>/tree.txt`. If your harness saved a large result to a file, `_uf.py tree <that file> out/<board>/tree.txt` extracts it, with no retyping. The shortest form is one line per child, `<node id> <board>:<key>`: leave out the rest of the name and the `... N children` lines.
   - Don't use `get_children` for this: it stops at 100 children, and `--drift` refuses a cut list.
2. **Drift:** `python3 specs/<spec>.py --drift out/<board>/tree.txt`. This puts node ids into `out/<board>/sync/plan.json` and prints:
   - **unkeyed:** elements someone added by hand, with their node ids.
   - **missing:** keyed elements someone deleted.
   - Drift can't see edits *inside* an element (changed text, colour or position). If the board has been open to other people, ask whether they edited it by hand.
   - If drift shows hand edits, show them to the user before changing anything. They choose:
     - **keep:** fold the edit into the spec (a new node, a changed note), re-render, and run drift again;
     - **discard:** delete the unkeyed nodes (`delete_nodes`) along with the plan's deletes.
3. **Run the ops.** `python3 design/user-flow/specs/_uf.py ops <board>` (add `--discard` to also delete the hand-added nodes) prints every call below with its arguments ready to paste, in order. What each step is:
   - `delete`: one `delete_nodes` call with every `node`.
   - `rename`: one `rename_nodes` call: `{nodeId: node, name: name}` for each. (The element didn't change, only its key.)
   - Placed boards: before the replaces, one `move_nodes` takes the placed screens out of the cards being replaced (to the artboard); after them, each goes back into its new card's `slot · …` node. `ops` prints both steps, and says when slots are left empty (stage and place them).
   - `replace`: `write_html(mode='replace', targetNodeId=node, html=<file>)`, one call each. Note the new node id it returns. `write_html(replace)` keeps the old node's position, so every replace also needs its `left`/`top` set (next step).
   - `move` and replaced positions: one `update_styles` call, one entry per node: `{nodeIds: [node], styles: {left: '<left>px', top: '<top>px'}}`. Use the new node ids for replaced elements.
   - `insert`: each `ins_NN.html` file with `write_html(mode='insert-children', targetNodeId=<artboard>)`.
   - If `size_changed`, set the artboard's width and height with `update_styles`.
   - 7 or more replaces: ask the user whether to use a subagent. If yes, hand them to one subagent with the replace prompt below (the `ops` lines are its input); if no, run them yourself in order.
4. **Check:** screenshot each changed node at scale 1 (get_screenshot works per node). A whole-board screenshot is capped at 2000px, so use it only for layout, never to read labels.
5. **Commit:** `python3 specs/<spec>.py --commit <artboard id>`.

A library screen changed and the maps should show the new version: `_uf.py stale <board> <node id…>` (or `all`), then sync. Those elements are replaced with fresh copies.

When the plan is all zero, there is nothing to paint. Still run drift if the board may have been edited by hand, and say so either way. Commit only if the plan line mentions a renderer change (`renderer 0.2.0 → 0.3.0`), so the board records the new version.

If a target is missing (the warning in step 2), or more than about 70% of the elements are replaced or inserted, paint in full instead: delete the artboard's children, paste `full/`, commit.

## Paste subagent prompt (only when the user allows subagents; use exactly this; always run it on Sonnet 5.5 at low effort: `model: "sonnet"`, and say "low effort" at the top of the prompt)
> You are pasting pre-generated HTML into a Paper design file. Do exactly this and nothing else.
> First load the tool: call ToolSearch with query "select:mcp__paper__write_html" (max_results 1).
> Then, for each file in this order: <absolute paths>
> 1. Read the file.
> 2. Call mcp__paper__write_html with fileId "<file id>", targetNodeId "<artboard id>", mode "insert-children", and html set to the file's contents EXACTLY, byte for byte. Do not reformat, shorten, fix or change anything.
> Do not call any other Paper tool. If a write fails, retry that same file once. If it fails again, stop and report the file and the error.
> When done, reply with one line per file: the file name and "ok" or the error.

## Replace subagent prompt (only when the user allows subagents; use exactly this)
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
