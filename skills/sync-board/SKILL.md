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
   - `config.json` → `maps` lists every board with its spec and artboard.
2. **Render:** `python3 specs/<spec>.py`. Read the plan line.
   - **`paint in full`:** no committed state yet. Follow "First paint". If the artboard exists but is unkeyed (painted before sync), delete its children first. Tell the user that's happening.
   - **`N insert · N replace · N delete`:** follow "Sync".
   - **`0 · 0 · 0`:** nothing to do. Say so.
3. **Drift first, always:** get_children, save the JSON to `out/<board>/children.json`, then run `--drift`. If it reports unkeyed or missing elements, show them. Ask whether to keep the hand edits (fold them into the spec, then re-render) or overwrite them. Don't silently overwrite someone's work.
4. **Run the ops** from `out/<board>/sync/plan.json`: deletes in one call, then replaces, then inserts. Resize the artboard if `size_changed`.
5. **Check:** screenshot the areas that changed, then the whole board.
6. **Commit:** `python3 specs/<spec>.py --commit <artboard id>`. If this is a new board, record it in `config.json`.

## Report
One line per board: "j2 · 1 replaced (panel) · 0 hand edits · committed". If the renderer version changed since the last commit, say so. A version bump can change unchanged boards.
