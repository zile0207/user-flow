# Design review (explore-design runs this twice)

Run it before showing a round's directions, and again before confirming one. Fix what fails in the spec (or in `ui_kit.py`) before the user sees it. List anything you chose not to fix under the direction's "Costs".

**Fit**
- It does every MUST DO point in the brief. Check each point off against a specific screen.
- It connects to the node before and the node after on the map. The first thing on screen follows from what the person just did.
- The edge case screen shows a real edge case from the need, not a restyled main state.

**The app's rules** (`config.json` → `rules`)
- Every line of copy follows `rules.copy`: vocabulary, banned words, what not to guess.
- The behaviour follows `rules.product`: what may be asked, when, and in what order.
- Data comes from the persona's story: real names, times, places and amounts. No lorem ipsum, no invented prices.

**Craft**
- Everything is built from `ui_kit.py` parts. No colours, sizes or fonts that aren't in the kit.
- Text contrast is at least 4.5:1 for body text and 3:1 for large text. Check every muted grey on its background.
- Tap targets are at least 44 × 44. The primary action is in thumb reach, in the lower half.
- One primary action per screen. Secondary actions look secondary.
- Nothing clipped or overlapping in the screenshot, at the device size in `theme.device`.

**Difference** (round review only)
- A, B and C differ in size, how much happens, or what the person decides. If two are the same idea in different styles, replace one.

Where a check fails the same way on the app's own confirmed screens (for example white text on the brand colour), record it under Costs rather than failing the direction, and say it's an app-wide issue.
