# Exploration board

Every exploration is `uf.explore.render(SPEC, P.out('explore_<id>'))` from `specs/explore_<id>.py`. The layout is fixed:
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
    'where': [('outside'|'this'|'screen', top, main[, sub]), ...],   # before → this → after
  },
  'refs_source': 'user' | 'mobbin',
  'refs': [{'img': P.refs_dir + '/x.png', 'name': 'App', 'take': 'what to take from it', 'url': '...'}],   # 3 to 6
  'rounds': [{'date': 'Mon 28 Sep', 'ask': None | 'what the user asked', 'directions': [
      {'letter': 'A', 'from': None | 'A', 'title': '...', 'idea': 'one sentence',
       'good': '...', 'costs': '...', 'inspired': '...',
       'screens': [{'label': 'Main state', 'html': phone(...)}, {'label': 'Edge case', 'html': phone(...)}]}]}],
}
if __name__ == '__main__':
    render(SPEC, P.out('explore_n2_1'))
```

## Rules
- **Letters are unique across the board.** Round 1 is A, B and C. Later rounds carry on with D, E, F… An iteration is a new letter with `'from': 'A'`. Screens are `<letter>·<n>`.
- **Each direction has 1 to 3 screens.** Screen 1 is the main state. The others are edge cases taken from the need, and each direction shows a different one.
- **Directions differ in substance:** size, how much happens, what the user decides. Not colour.
- **Match the confirmed look.** Read the nearest confirmed neighbour with get_jsx, and add any missing part to `ui_kit.py`. No one-off HTML inside a spec.
- **References come from the user first:** images or links in the prompt, or a frame named `Refs · <id>`. If there are none, use Mobbin: 2 or 3 queries aimed at the job the screen does. Keep 3 to 6, each with one line on what to take from it.
- **The board** is an artboard named `Explore · <id> · <title>` on the maps page, to the right of the other maps. Record it in `config.json` → `maps.explorations`.

## The three replies after a round
1. **Iterate on X:** add a round with `'from': 'X'` directions, give them the next letters, and put the user's words in `ask`.
2. **More variants:** add a round of new directions with the next letters.
3. **Confirm X:**
   1. Set `status` to confirmed and re-render. This draws the outline and CHOSEN pill on the chosen direction, the CONFIRMED bar, and the header state. Only the header, the chosen direction's heading, the outline and the bar change, so you can replace just those nodes.
   2. Export `X·1` as a PNG and save it as `img/<id with - for ·>_X.png` (e.g. `N2-1_A.png`).
   3. Run `P.set_gap(id, state='explored', chosen='X', round=n, img='N2-1_X', board='<artboard>')`.
   4. Swap the gap's card on every map that shows it. Either re-render that map, or replace just the card node with `explored_card(SPEC, x, y, png)`, then update the counts.

Keep the journey card's tag in step: "EXPLORING, ROUND n" while a board is open.
