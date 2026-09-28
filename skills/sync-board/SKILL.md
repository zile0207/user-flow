---
name: sync-board
description: Bring a Paper board in line with its spec by changing only what differs (insert, replace, delete), after checking the board for hand edits. Use after any spec, gap or question change, when a board looks out of date, or when the user asks to update, refresh, repaint or sync a map or exploration.
---

# sync-board

The only way boards change on the canvas. Other skills edit specs and registries, then run this.

**Plugin root:** this skill's real directory, two levels up. Read `references/sync.md` (all of it).
**Project:** `design/user-flow/`. If it's missing, run **init**.

## Steps
1. **Which boards:** the one named in the prompt, or every board a change touched.
   - A gap change touches every map that shows the gap, plus the master map.
   - A question change touches its map.
   - `config.json` → `maps` lists every board with its spec and artboard. `_uf.py status` lists the ones out of date.
2. **Render:** `python3 specs/<spec>.py`. Read the warnings and the plan line.
   - **Warnings** (labels overlapping, a row with no label): fix them in the spec first, then render again.
   - **`paint in full`:** no committed state yet. Follow "First paint" in `sync.md`. If the artboard exists but is unkeyed (painted before sync), delete its children first and tell the user.
   - **`N insert · N replace · N move · N rename · N delete`:** follow "Sync".
   - **All zero:** nothing to paint. Still check for hand edits (step 3) unless the board was painted in this session, and say what you found. Commit only when the line shows a renderer change, so the board records the new version.
3. **Drift, before any change:** `get_tree_summary(<artboard>, depth 1)` → `out/<board>/tree.txt` → `python3 specs/<spec>.py --drift out/<board>/tree.txt`. Never use `get_children` for this (it stops at 100).
   - Unkeyed or missing elements are hand edits. Show them and ask: **keep** (fold into the spec, re-render, drift again) or **discard** (delete the unkeyed node ids it printed, with the plan's deletes). Don't silently overwrite someone's work.
   - Drift can't see text or style changed inside an element. If people other than agents edit this board, ask.
4. **Run the ops:** `python3 design/user-flow/specs/_uf.py ops <board>` (`--discard` to delete hand-added nodes too) prints each Paper call with its arguments, in order: delete, rename, replace, one `update_styles` for moves and replaced positions, insert, the artboard size. Paste them; don't rebuild them by hand.
5. **Check:** screenshot each changed node at scale 1 (whole-board shots are too small to read). After the commit, re-render: the plan must be all zero.
6. **Commit:** `python3 specs/<spec>.py --commit <artboard id>`. If this is a new board, record it in `config.json`. If the renderer version changed, set `config.json` → `plugin_version` to the new one once every board is synced.

## Report
One line per board: "j2 · 7 replaced, 30 moved, 2 inserted · 1 hand edit discarded · committed". If the renderer version changed since the last commit, say so: a version bump can change boards whose spec didn't.
