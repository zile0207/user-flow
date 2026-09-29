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

## 2. The screens become library frames
Each screen of the chosen direction becomes its own artboard on the **promote page** (`sources.paper.promote_page`, the library page by default), named with a stable id, `X1·1 · Google failed`, like every other library screen. Ids are never reused or renumbered; new gaps get the next numbers.
- Say that this writes to the library page and ask first, unless the user already said to go ahead.
- One spec per journey, `specs/promoted_j<n>.py`:
```python
from _uf import P
from uf.promote import PromotedChapter
C = PromotedChapter(P, 1)          # prefix 'X' (config.json → promote_prefix)
C.add('N1·3')                      # every promoted gap of this journey, in map order
if __name__ == '__main__':
    C.render('Tue 29 Sep 2026')
```
- Render it: it lists the frames to make (name, 390 × 844, HTML file). Nothing goes into the registry yet.
- For each: `create_artboard(pageId = promote page, name, width, height)`, then `write_html(insert-children)` with the file. Put them anywhere free for now; the master layout places them.
- Record them: `_uf.py promoted promoted_j<n> <node id of each frame, in order>`. The gap becomes `promoted`, with its `screen_ids`, `screen_nodes` and `node` (the first frame).
- **Tokens:** if the project has a token file, read the new frames (`get_tree_summary` + `get_jsx`, then `_uf.py bind-from-transcript`) and run `_uf.py bind-plan promoted_j<n> <node id…>`. It should find nothing to bind; bind whatever it finds (**bind-tokens**) before reporting.
- Record the spec in `config.json` → `maps.promoted`: `{"journey": <n>, "spec": "specs/promoted_j<n>.py", "page": "<page id>"}`.

## 3. Update the maps
- `_uf.py promoted` already added the frames to `library.json`: no re-index needed.
- Re-render and **sync-board** every map that shows the gap. The card becomes the promoted frame (a live copy) with its new id.
- Re-run the master layout (`specs/master.py`, then `_uf.py layout-ops master`): the promoted frames take the dashed gap frame's place in their area, and only that area's changes are applied. Then `_uf.py layout-commit master <tree>`: pass the page's tree (a saved result, or only its `master:` lines as `<id> <name>`) so every generated frame keeps its id.
- Mark the exploration `promoted` in `config.json` → `maps.explorations`.

## 4. Report
- New screen ids.
- Where the chapter is.
- Which maps changed.
- One line for developers: "Build X1·1 and X1·2 from the <library page name> page. Journey 1 shows where they sit."
