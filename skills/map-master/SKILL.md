---
name: map-master
description: Plot every screen in the app on one master map, grouped by area, with every known gap in place. Use when the user wants to see all screens, the whole app, an inventory of what exists and what is missing, or a starting point before mapping journeys.
---

# map-master

The master map is the inventory. It shows every screen from every source, grouped by area, with every needs-design gap in its area. It has no arrows: journeys and flows carry those.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (Three levels, Master map items) and `references/project-and-paper.md`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Collect every screen
Merge all the sources in `config.json`:
- **Paper or Figma screens page:** every screen frame, with its id (chapter·step or frame name) and node id.
- **Codebase routes:** every route. Match each one to its design screen by name and purpose. A route with no design becomes a card with `ref` = the route and a code screenshot if available. If there's no image, make it a gap titled "<route> · needs a design", with the need "Built in code, no design yet".
- **Gaps:** everything in `gaps.json`.

Drop exact duplicates: the same screen shown twice in a story counts once. Keep states that differ (empty, error, loading) as separate screens.

## 2. Group into areas
- An area is a tab, a section or a route group (e.g. Onboarding, Explore, Links, Boards, Plans, Profile, The top, Shell).
- Order the areas the way a person meets them.
- Each area gets a subtitle (source chapters or routes) and its entry points in words.

## 3. Spec, render, paste
- Export each screen once: `img/<node id>.png`, 1x.
- Write `specs/master.py`:
```python
from _uf import P
from uf.master import MasterMap
M = MasterMap(P, columns=5)
M.area('Onboarding', 'A1 · app/(auth), app/(onboarding)', [('card', '1CH7', 'A1·1', 'Discover'), ('gap', 'N1·2'), ...],
       entries='first launch, sign out')
...
if __name__ == '__main__':
    M.render('<Project> · every screen', '<n> areas · <date>', '<one sentence: what this map is>')
```
- Render, then paste per `references/project-and-paper.md`. The artboard is named `Master map`, placed first on the maps page. Record it in `config.json` → `maps.master`.

## 4. Audit
Run **audit-flow** on the master map at inventory level: areas with no empty, error or loading states, routes without designs, designs without routes. New gaps join the registry under the journey for that area, or `N0·n` if no journey covers it yet.

## 5. Report
- The counts: designed, to design, after MVP, areas.
- The 3 areas with the most gaps.
- The suggested next journeys to map. These are the areas with the most screens or gaps that don't have a journey yet.
