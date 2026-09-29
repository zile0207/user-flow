---
name: explore-design
description: Design a needs-design gap (N2·3 style id) on its own exploration board. Gathers references (the user's, else Mobbin), builds 3 genuinely different directions in the app's real UI, then iterates, adds variants or confirms one, and swaps the gap card on the maps for the chosen screen. Use when the user says explore, design this gap, iterate on a direction, more variants, or confirm a direction.
---

# explore-design

**Plugin root:** this skill's real directory, two levels up. Read `references/explore-board.md` (all of it), `references/design-review.md`, `references/sync.md` and `references/project-and-paper.md`. Follow `config.json` → `rules` in every line of copy. Reference spec: `templates/examples/explore_n2_1.py`.
**Project:** `design/user-flow/`. If it's missing, run **init**. It also needs `ui_kit.py`: if it's missing or thin, extend it from the nearest confirmed screen first.

## 0. Which gap, and which step
- **An id in the prompt** (`N2·3`): use it.
- **A title instead** ("design the email sign-in"): match it against the titles in `_uf.py gaps`. One clear match: say which ("That's N1·2 Email sign-in") and go on. Several: ask, listing only those.
- **"Confirm X", "iterate on X", "more variants" without an id:** if exactly one board is open (a gap in state `exploring`), it's that one. Otherwise ask which exploration.
- **Nothing to go on:** run `_uf.py gaps --state todo` and `--state exploring`, show the list grouped by map (the persona's-path gaps come first), and ask which one. Don't guess.
- **The id already has a board** (`config.json` → `maps.explorations`): the prompt is a reply to a round. Go to step 5.
- **Already designed?** Run `_uf.py find --gap <id>` and screenshot the best hits. If the library already has this screen, say so: offer to mark the gap `found` (`_uf.py set-gap <id> state=found node=<node> ref=<ref>`, then sync the maps) instead of exploring.
- **Blocking questions:** run `_uf.py blocking <id>`. If an open question blocks this gap (Q1·3 "code or password?" blocks N1·2), ask it first, with your recommendation. Carry on only when it's answered (record it with **answer-questions**), or when the user says to explore both answers, one direction each.
- Otherwise, start at step 1.

## 1. Understand the gap
- From `gaps.json`: title, need, where.
- From the map spec, the nodes before and after it: what the person just did, and where they go next. Those neighbours set the context and the look. In the brief's "where it sits", a neighbouring screen is its node id (a live copy), never an image.
- Write the brief: the need in 2 or 3 sentences, 3 to 6 checkable "must do" points, and "where it sits" (before → this → after).

## 2. References
- **The user's first:** images or links in the prompt, or a frame named `Refs · <id>` on the maps page.
- **Otherwise Mobbin:** 2 or 3 searches aimed at the job, not the look ("share extension saving to an app", not "clean card"). Keep 3 to 6. Download the images into `refs/` (`curl -L`, the links redirect; convert webp to png, e.g. `sips -s format png in.webp --out out.png`). Each one gets one line on what to take from it.

## 3. Three directions
- Read the nearest confirmed screen with get_jsx and extend `ui_kit.py` with any part you need. Screens are built only from ui_kit parts.
- **Tokens:** when the project has a token file (`sources.paper.tokens`), ui_kit parts use `var(--token)` for every colour, size, radius and space (a transparent colour is `color-mix(in oklab, var(--token) N%, transparent)`). No hex values or bare pixel sizes that have a token.
- **A, B and C must differ in substance:** how big, how much happens, what the person decides. Each gets:
  - one idea sentence
  - a main-state screen plus an edge case from the need (a different edge case per direction)
  - good, costs, and inspired by
- Use the persona's real data from the story: names, times, places.

## 4. Build the board
- Write `specs/explore_<id>.py`, following the example, and render it.
- Run the **design review** (`references/design-review.md`) and fix what fails before anyone sees it.
- Create the artboard `Explore · <id> · <title>` on the **explore page** (`sources.paper.explore_page`), right of the other explorations, at the printed size. Paint it in full (`references/sync.md` → First paint: commit straight after pasting), then screenshot and review.
- Update the registry: `_uf.py set-gap <id> state=exploring round=1 board=<artboard>`. Add the board to `config.json` → `maps.explorations`. Re-render and **sync-board** the maps that show the gap, so their cards read "EXPLORING, ROUND 1".
- Tell the user their options: **confirm X**, **iterate on X: <what to change>**, **more variants**, or **mix** ("A's size with B's places"). Give your pick and one reason.

## 5. Replies
Follow `references/explore-board.md` → "The three replies" exactly:
- **Iterate / mix / more variants:** a new round below, with the next letters, `from` set, and the ask recorded. Review it, re-render, then **sync-board** the board (only the new round and the bar change). Set `round` in the registry.
- **Confirm X:**
  - Run the design review on the chosen direction.
  - Set the spec's `status` to confirmed, re-render, then **sync-board** the board (header, chosen heading and bar are replaced; the outline is inserted).
  - Find the node id of the chosen screen `X·1` on the board (`get_tree_summary` of `<board>:dir<X>screens`, depth 2).
  - Run `_uf.py set-gap <id> state=explored chosen=X round=<n> node=<that node id>`. The maps show a live copy of that frame, never an image.
  - Re-render and **sync-board** every map that shows the gap. The card and the counts follow the registry.
- If the chosen design adds new states the maps didn't have, run **audit-flow** on that journey.
- Then offer **promote-design**, which puts the confirmed screens on the screens page for developers.
