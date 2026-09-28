---
name: map-states
description: Map every state one piece of UI can show (a top card, banner, now-playing bar, status pill), in priority order, with when each shows, when it ends and what it gives way to, and any open question about which state should win. Use when a surface shows one thing at a time, when states compete, or when the user asks what shows when.
---

# map-states

Some UI shows one thing at a time and several things compete for it. A journey can't show that well. A state map lists every state in priority order, with the rule that picks the winner.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (State map rows) and `references/sync.md`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Collect the states
- Search every source for the element: screens page chapters, journey specs, the codebase (a component, its props and conditions).
- For each state record:
  - **name**
  - **shows when:** the trigger or condition
  - **until:** what ends it
  - **variants:** sizes or forms, each designed (a card) or not (a gap)
  - **gives way to:** which states can take over
- A state that appears in the rules but was never designed becomes a gap under the journey that owns it: `_uf.py add-gap <journey no> "<title>" "<need>"`, once, from the shell.

## 2. Priority and the rule
- Put the states in priority order. Then write the rule in one sentence, for example "Highest priority that applies wins. Ties: newest first. The persona can swipe a state away once."
- Where the sources disagree (two chapters show different winners for the same moment), don't pick one. Reuse the question if it's already in `_uf.py questions`; otherwise add it under the journey that owns the surface (state maps have no panel of their own): `_uf.py add-question J<n> "<text>"`. Link it to the state with `question=` (one id, or a list). It shows in amber on the row. Suggest running **answer-questions**.

## 3. Spec, render, paint
- Write `specs/states_<slug>.py`:
```python
from _uf import P
from uf.states import StateMap
S = StateMap(P, 'The top', 'Highest priority that applies wins. Ties: newest first.')
S.state('link_failed', 'A link failed', 1, 'Argo could not read a link', 'Try again or Not now',
        [('card', '24MN', 'J3·5', 'Widget'), ('card', '24NZ', 'J3·6', 'Half')], gives_way_to=['offline'], question='Q2·1')
...
if __name__ == '__main__':
    S.render('The top · every state', '<n> states · <date>', '<one sentence>', 'states_top')
```
- Export any screen images you need (batches of at most 12). Render, then create the artboard `States · <element>` on the maps page, after the flows. Paint and commit it (`sync.md` → First paint), screenshot and review, then record it in `config.json` → `maps.states` as `{"element": "<element>", "spec": "specs/states_<slug>.py", "artboard": "<id>"}`.

## 4. Report
- The rule.
- The states in order.
- The conflicts turned into questions.
- New gaps.
