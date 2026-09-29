# Exploration board

Every exploration is `uf.explore.render(P, 'explore_<id>', SPEC)` from `specs/explore_<id>.py`. Boards go on the explore page (`config.json` → `sources.paper.explore_page`). The layout is fixed:
- a header bar
- the left column: the gap, must do, where it sits, references
- rounds on the right: directions side by side, each with its screens, labels and notes
- a pick bar, or a confirmed bar once one is chosen

## Spec

```python
from _uf import P
from uf.explore import render
from ui_kit import *            # the project's screen parts. Build screens only from these.

SPEC = {
  'id': 'N2·1', 'title': 'Share to Argo', 'source': 'from Journey 2, row 2',
  'journey': {'name': 'Journey 2', 'artboard': '<id>', 'card_xy': (x, y)},
  'status': {'state': 'exploring', 'date': 'Mon 28 Sep 2026'},
  #   confirmed → {'state': 'confirmed', 'chosen': 'A', 'round': 1, 'date': '...'}
  'brief': {
    'needs': 'the gap\'s need, expanded to 2 or 3 sentences',
    'musts': ['3 to 6 checkable points'],
    'where': [('outside'|'this'|'screen', top, main[, sub]), ...],   # before → this → after; for 'screen', top = the frame's node id
  },
  'refs_source': 'user' | 'mobbin',
  'refs': [{'img': P.refs_dir + '/x.png', 'name': 'App', 'take': 'what to take from it', 'url': '...'}],   # 3 to 6
  'rounds': [{'date': 'Mon 28 Sep', 'ask': None | 'what the user asked', 'directions': [
      {'letter': 'A', 'from': None | 'A', 'title': '...', 'idea': 'one sentence',
       'good': '...', 'costs': '...', 'inspired': '...',
       'screens': [{'label': 'Main state', 'html': phone(...)}, {'label': 'Edge case', 'html': phone(...)}]}]}],
}
if __name__ == '__main__':
    render(P, 'explore_n2_1', SPEC)
```

## Rules
- **Letters are unique across the board.** Round 1 is A, B and C. Later rounds carry on with D, E, F… An iteration is a new letter with `'from': 'A'`. Screens are `<letter>·<n>`.
- **Each direction has 1 to 3 screens.** Screen 1 is the main state. The others are edge cases taken from the need, and each direction shows a different one.
- **Directions differ in substance:** size, how much happens, what the user decides. Not colour.
- **Match the confirmed look.** Read the nearest confirmed neighbour with get_jsx, and add any missing part to `ui_kit.py`. No one-off HTML inside a spec.
- **References come from the user first:** images or links in the prompt, or a frame named `Refs · <id>`. If there are none, use Mobbin: 2 or 3 queries aimed at the job the screen does. Keep 3 to 6, each with one line on what to take from it.
- **The board** is an artboard named `Explore · <id> · <title>` on the explore page, to the right of the other explorations. Record it in `config.json` → `maps.explorations`.
- **Review** every round with `design-review.md` before showing it, and the chosen direction again before confirming.

## The three replies after a round
1. **Iterate on X:** add a round with `'from': 'X'` directions, give them the next letters, and put the user's words in `ask`.
2. **More variants:** add a round of new directions with the next letters.
3. **Confirm X:**
   1. Set `status` to confirmed and re-render, then **sync** the board (`sync.md`). Sync replaces only the header, the chosen direction's heading and the bar, and inserts the outline.
   2. Find the node id of the chosen screen `X·1` on the board: `get_tree_summary` of the `<board>:dir<X>screens` element (depth 2).
   3. Run `_uf.py set-gap <id> state=explored chosen=X round=<n> node=<that node id> board=<artboard>`. Maps show a live copy of that frame, never an image.
   4. Re-render and **sync** every map that shows the gap. The registry change swaps the card and the counts.
   5. Offer **promote-design**, which moves the confirmed screens onto the screens page so developers build from one place.

Keep the journey card's tag in step: "EXPLORING, ROUND n" while a board is open.
