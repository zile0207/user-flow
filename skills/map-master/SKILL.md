---
name: map-master
description: Plot every screen in the app on one master map, grouped by area, with every known gap in place. Use when the user wants to see all screens, the whole app, an inventory of what exists and what is missing, or a starting point before mapping journeys.
---

# map-master

**With a library page, the master map is that page, organised** (`uf.library_layout`): every screen frame moves into its area, in the order the persona meets them, under a title band, with a dashed frame for each screen still to design. Nothing is copied: copying every screen doubles the file and hits Paper's size limit. Frames keep everything but their position; the page's other frames (notes, bands) stay where they are. Say so and ask before the first layout, since it rearranges the page. The layout can also go on a page of its own (`render(..., to_page=…)`): the frames move there with their ids, that page becomes the library, and the old page can be retired. Without a library page, use `uf.master.MasterMap` (a generated board of copies) and keep it small.

The master map is the inventory. It shows every screen from every source, grouped by area, with every needs-design gap in its area. It has no arrows: journeys and flows carry those.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (Levels, Master map items) and `references/project-and-paper.md`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Collect every screen
Merge all the sources in `config.json`:
- **The library page** first (`library.json`; index it if missing): every confirmed screen, with its node id. Then the curated screens page (the story), for context and for screens the library lacks. Figma: the screens page's frames. Each screen's id and node id. Ids follow `references/project-and-paper.md` → Screen ids. When you need the fallback (no step numbers, restarting rows, old names), write the rule you used into `config.json` → `screen_ids`.
- For a big page, list the screens with a script-like pass: get_basic_info for the artboards, then get_tree_summary per chapter. Save the list to `out/screens.json` as you go, so it survives a long run.
- **Codebase routes:** every route. Match each one to its design screen by name and purpose. A route with no design becomes a gap titled after the screen (for example "Constraints"), with the need "Built in code at <route>, no design yet".
- **Gaps:** everything in `gaps.json`.

Drop duplicates by the rule in `references/project-and-paper.md` → Duplicates: the same screen shown twice in a story counts once. Keep states that differ (empty, error, loading) as separate screens.

## 2. Group into areas
- An area is a tab, a section or a route group (e.g. Onboarding, Explore, Links, Boards, Plans, Profile, The top, Shell).
- Order the areas the way a person meets them. The layout keeps the order you add them in (left to right, then the next row).
- Each area gets a subtitle (source chapters or routes) and its entry points in words.

## 3. Spec, render, paste
- Every card is `('card', <node id>, <ref>, <title>)`: a live copy of the real frame, never an image. Take the node from the library where the screen exists there.
- Write `specs/master.py`:
```python
from _uf import P
from uf.master import MasterMap
M = MasterMap(P, columns=5)
M.area('Onboarding', 'A1 · app/(auth), app/(onboarding)', [('card', '1CH7', 'A1·1', 'Discover'), ('gap', 'N1·2'), ...],
       entries='first launch, sign out')
...
if __name__ == '__main__':
    M.render('<Project> · every screen', '<n> areas · <date>', '<one sentence: what this map is>')   # board 'master'
```
- **Library layout:** `specs/master.py` uses `LibraryLayout(P, cols, origin, per_row)` and `L.area(name, sub, groups, gaps, entries)`. Render it, then `_uf.py layout-ops master` prints every Paper call (moves in batches of 100, then the bands and gap frames to make). `layout-ops` prints only what changed since the last `_uf.py layout-commit master <tree>` (pass the page's tree, or just its `master:` lines as `<id> <name>`, so the generated frames keep their ids).
- **Generated board (no library):** render, then paint per `references/sync.md` → First paint (commit straight after pasting). The artboard is named `Master map`, on `sources.paper.master_page` if the project has one, otherwise first on the maps page. Record it in `config.json` → `maps.master` as `{"spec": "specs/master.py", "artboard": "<id>"}`. Later changes go through **sync-board**.

## 4. Audit
Run **audit-flow** on the master map at inventory level: areas with no empty, error or loading states, routes without designs, designs without routes. New gaps join the registry under the journey for that area, or `N0·n` if no journey covers it yet. Questions about the whole app go in as `_uf.py add-question M "<text>"` and render in the master map's panel.

## 5. Report
- The counts: designed, to design, after MVP, areas.
- The 3 areas with the most gaps.
- The suggested next journeys to map. These are the areas with the most screens or gaps that don't have a journey yet.
