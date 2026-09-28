---
name: explore-design
description: Design a needs-design gap (N2·3 style id) on its own exploration board. Gathers references (the user's, else Mobbin), builds 3 genuinely different directions in the app's real UI, then iterates, adds variants or confirms one, and swaps the gap card on the maps for the chosen screen. Use when the user says explore, design this gap, iterate on a direction, more variants, or confirm a direction.
---

# explore-design

**Plugin root:** this skill's real directory, two levels up. Read `references/explore-board.md` (all of it) and `references/project-and-paper.md`. Reference spec: `templates/examples/explore_n2_1.py`.
**Project:** `design/user-flow/`. If it's missing, run **init**. It also needs `ui_kit.py`: if it's missing or thin, extend it from the nearest confirmed screen first.

## 0. Which gap, and which step
- **No id in the prompt:** list the gaps that are todo or exploring from `gaps.json`, grouped by map, with the persona's-path ones first, e.g. "N1·2 Email sign-in (Journey 1, row 2)". Ask which one. Don't guess.
- **The id already has a board** (`config.json` → `maps.explorations`): the prompt is a reply to a round. Go to step 5.
- Otherwise, start at step 1.

## 1. Understand the gap
- From `gaps.json`: title, need, where.
- From the map spec, the nodes before and after it: what the person just did, and where they go next. Those neighbours set the context and the look.
- Write the brief: the need in 2 or 3 sentences, 3 to 6 checkable "must do" points, and "where it sits" (before → this → after).

## 2. References
- **The user's first:** images or links in the prompt, or a frame named `Refs · <id>` on the maps page.
- **Otherwise Mobbin:** 2 or 3 searches aimed at the job, not the look ("share extension saving to an app", not "clean card"). Keep 3 to 6. Download the images into `refs/`. Each one gets one line on what to take from it.

## 3. Three directions
- Read the nearest confirmed screen with get_jsx and extend `ui_kit.py` with any part you need. Screens are built only from ui_kit parts.
- **A, B and C must differ in substance:** how big, how much happens, what the person decides. Each gets:
  - one idea sentence
  - a main-state screen plus an edge case from the need (a different edge case per direction)
  - good, costs, and inspired by
- Use the persona's real data from the story: names, times, places.

## 4. Build the board
- Write `specs/explore_<id>.py`, following the example, and render it.
- Create the artboard `Explore · <id> · <title>` on the maps page, right of the other boards, at the printed size. Paste, screenshot and review.
- Update the registry: `P.set_gap(id, state='exploring', round=1, board='<artboard>')`. Add the board to `config.json` → `maps.explorations`. Set the gap card's tag on the maps to "EXPLORING, ROUND 1" (re-render, or edit the tag text).
- Tell the user their options: **confirm X**, **iterate on X: <what to change>**, **more variants**, or **mix** ("A's size with B's places"). Give your pick and one reason.

## 5. Replies
Follow `references/explore-board.md` → "The three replies" exactly:
- **Iterate / mix / more variants:** a new round below, with the next letters, `from` set, and the ask recorded. Set `round` in the registry.
- **Confirm X:**
  - Update the board (outline, CHOSEN, CONFIRMED bar, header).
  - Export `X·1` to `img/<id>_X.png`.
  - Run `P.set_gap(id, state='explored', chosen='X', round=n, img=...)`.
  - Swap the gap card on every map that shows it, then update the counts.
- If the chosen design adds new states the maps didn't have, run **audit-flow** on that journey.
