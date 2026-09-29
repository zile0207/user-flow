---
name: promote-design
description: Move a confirmed exploration onto the app's confirmed screens page as real screens with stable screen ids (X2·1 style), so developers build from one place, and switch the gap's card on every map to the promoted screen. Use after a direction is confirmed, or when the user asks to promote, hand off, publish or move a confirmed design to the screens page.
---

# promote-design

A confirmed direction lives on its exploration board until it's promoted. Promotion puts its screens on the screens page (the page developers build from), in a chapter for that journey, with ids that never change.

**Plugin root:** this skill's real directory, two levels up. Read `references/sync.md` and `references/project-and-paper.md`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. What to promote
- The gap id comes from the prompt. If there isn't one, list the gaps with `state == 'explored'` and ask.
- Only confirmed gaps can be promoted, meaning ones with an exploration board and a chosen direction. For a gap that's only exploring, point to **explore-design** first.
- Run **design-review** (`references/design-review.md`) on the chosen screens one last time. Promotion means developers start building.

## 2. The chapter
- Each journey gets one promoted chapter: `X<journey> · From explorations (Journey <n>)`, spec `specs/promoted_j<n>.py`:
```python
from _uf import P
from uf.promote import PromotedChapter
C = PromotedChapter(P, 2)          # prefix 'X' by default; set config.json → promote_prefix to change it
C.add('N2·1')                      # every promoted gap for this journey, in the order they appear on the map
if __name__ == '__main__':
    C.render('Screens confirmed in explorations for Journey 2 · Collecting.', 'Mon 28 Sep 2026')
```
- The render gives each screen a stable id (X2·1, X2·2, …). It stores the ids in `gaps.json` (`screen_ids`, `chapter`) and sets the gap to `promoted`. Ids are never reused or renumbered. Add new gaps at the end.
- **First time:** create the artboard on the **promote page** (`sources.paper.promote_page`; if unset, the library page, else the screens page), after the existing content, at the printed size. Paint it in full and commit (`sync.md` → First paint).
  - This is the only time the plugin writes to a screens page. Say so and ask before doing it, unless the user already said to go ahead.
  - Record the chapter in `config.json` → `maps.promoted`: `{"journey": <n>, "spec": "specs/promoted_j<n>.py", "artboard": "<id>", "page": "<page id>"}`.
- **Later:** **sync-board** the chapter.

## 3. Update the maps
- Point the gap at the promoted frame: find the node id of `<board>:screenX2_1` (`get_tree_summary` of the chapter, depth 1) and run `_uf.py set-gap <id> node=<that node id>`. The maps then show a live copy of the promoted screen, never an image.
- Re-index the library (`_uf.py library …`) so the promoted screens are in it.
- Re-render and **sync-board** every map that shows the gap, plus the master map. The card becomes a normal screen card with the new id and "Designed in Explore · N2·1 (A)".
- Mark the exploration done in `config.json` → `maps.explorations` (`state: promoted`).

## 4. Report
- New screen ids.
- Where the chapter is.
- Which maps changed.
- One line for developers: "Build X2·1 and X2·2 from the <screens page name> page. Journey 2 shows where they sit."
