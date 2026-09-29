# Maps: levels, nodes, arrows, layout

Every map is rendered by `lib/uf` from a spec in the project's `design/user-flow/specs/`. Don't hand-draw a map on the canvas. Write or edit the spec, render it, paste the chunks.

**Screens are real frames, never images.** Every screen on every board is a live copy of its Paper frame (`project-and-paper.md` → Screens on boards). Specs name screens by node id.

## Levels

| Level | Skill | Scope | Renderer | Arrows? |
|---|---|---|---|---|
| **State map** | map-states | Every state one piece of UI can show, in priority order | `uf.states.StateMap` | No. Rows sorted by priority, with shows-when, until and gives-way-to |
| **Master** | map-master | Every screen in the app, grouped by area (tab, section, route group) | `uf.master.MasterMap` | No. It's an inventory: what exists and what's missing. |
| **Journey** (segment) | map-journey | One area end to end, with every way through it (e.g. "Getting in", "Collecting") | `uf.jmap.Map` | Yes. A full flowchart. |
| **Flow** (JTBD) | map-flow | One job, start to done ("save a video and turn it into Saturday's plan"), crossing areas | `uf.jmap.Map` | Yes, one main row plus only the branches that change the outcome |

Rules across levels:
- A screen keeps one ID everywhere. It's the ID from the source (the Paper page's chapter·step, a route, or a Figma frame).
- A gap has one ID everywhere: `N<journey>·<n>` from `gaps.json`. A gap found in a flow or on the master map belongs to the journey that covers its area. A flow's legend explains ids as "N2·3 = gap 3 of journey 2". If no journey covers that area yet, use `N0·<n>` until one does.
- The master map shows every gap from `gaps.json` in its area. Journeys and flows show the gaps on their paths.

## Nodes (journey and flow maps)

| Method | Looks like | Use it for | Rules |
|---|---|---|---|
| `card(id, x, y, node, ref, title, note, jamie)` | A white card holding a live copy of the real frame | A designed screen | `node` = the frame's Paper node id, from the library page where it exists (never an image). `ref` = the screen ID. `note` = one line: what happens here. `jamie=True` puts the persona's path in the accent colour. |
| `gap(id, x, y, **P.g('N2·3'))` | A dashed card, "N2·3 · NEEDS DESIGN" | A screen or state that isn't designed | Always pull it from the registry with `P.g(gid)`, never type gap text into a spec. States: todo, exploring, explored, later. |
| `dia(id, cx, y, text, sys)` | A diamond | A decision | White = the user chooses. Ink (`sys=True`) = the app or the phone decides. It needs 2+ labelled exits (checked on render). |
| `sysbox(id, x, y, w, text, sub)` | A grey box tagged with the app's name | The app working in the background | Reading, building, syncing, sending. Not for screens. |
| `outside(id, x, y, w, text, sub)` | A dashed ink box, OUTSIDE | A step in another app or the OS | Share sheet, another app, Settings, email. |
| `pill(..., 'start')` | An ink pill | Where a path begins | The persona, the moment, the date. |
| `pill(..., 'exit')` | A white pill | Continues in another map | "→ 4 · Making a plan" |
| `pill(..., 'entry')` | A grey dashed pill | Comes from another step or map | "From 8 · Skip" |
| `pill(..., 'jump')` | A light pill, ↩ | Loops back to a far node | Instead of an arrow across the map |

**Master map items:** `('card', node, ref, title)` and `('gap', gid)`, grouped in `area(name, sub, items, entries)`. Areas are laid out in rows in the order you add them (`MasterMap(P, columns=5)`), so add them in the order a person meets them. Questions filed under map `M` (QM·n) render in a panel at the bottom. `M.library_area(name, sub, groups, gaps)` fills an area straight from `library.json`, so the master map follows the library when it's re-indexed.

**State map rows:** `state(key, name, priority, when, until, variants, gives_way_to, note, question)`.
- `variants` are up to 4 of `('card', node, ref, label)` or `('gap', gid, label)`: the sizes or forms the state takes, e.g. widget, half, page.
- `question` links an open Q id, or a list of them, which then show on the row in amber. State maps have no panel: file their questions under the journey that owns the surface (`add-question J3 …`).
- The board states the winning rule once, for example "Highest priority that applies wins. Ties: newest first."

## Spec skeleton (journey or flow)
```python
from _uf import P
from uf.jmap import Map, row_y
m = Map(<journey no>, P)
...nodes and arrows...
if __name__ == '__main__':
    m.render(P, 'j<no>', <width>, '<title>', '<right text>', '<one-sentence story>',
             [(1, "<PERSONA>'S PATH", '<date>', True), (2, '<THEME>', '', False)],
             P.panel('J<no>', x, y, w))          # decisions and open questions come from questions.json
```
Every render writes keyed elements, a full-paint set and a sync plan (see `sync.md`).

## Arrows
- `m.h(a, b)`: same row, left to right. `m.v(a, b)`: straight down, or up with `up=True`. `m.e([points])`: any route. Right angles only.
- **Colour:** `'coral'` is the persona's path (it renders in the project's accent colour). Everything else is grey.
- **Dashed** means remembered for later, or after MVP.
- **Labels** say what caused the step ("Taps Paste", "Yes", "About a minute"). Every exit of a decision is labelled, and so is any arrow whose cause isn't obvious from the two nodes. An arrow from a screen into the decision that follows it needs no label. Set `lw` so long labels wrap.
- **Keys:** an arrow's key names the two nodes it joins (`e_d1_g3`; an end on a line reads `bus`: `e_bus_g3`), so moving nodes moves arrows instead of redrawing them. A line that touches no node (the bus itself) needs `key='bus_row3'` on `m.e(...)`, or it's keyed by its coordinates. Keep node ids short and stable.
- `na=True`: no arrowhead. Use it for a stem into a bus, or a line merging into another line.
- **Crossings:** arrows carry a white halo, so a crossing reads as a hop. Keep them rare.

## Layout
- **Rows:** `row_y(n)` is row n's attach line. Card tops are 380, 1080, 1780…, 700 apart.
  - Row 1 is the persona's main path.
  - Lower rows hold other ways through, grouped by theme. A later persona path (another day) gets its own row with the accent colour and a date.
- **Spacing:** a card is 200 wide and a diamond 150. Leave 70 px between nodes with no label, 90–130 px with one. `m.seq(y, x, [...])` lays out a row for you.
- **Branches** drop straight down under their source (`m.under(src, y)`).
- **Fan-outs:** a stem down to a bus line 50 px above the target row, then one drop per card.
- **Lanes:**
  - Loops over row 1 use y = 345.
  - Long runs between rows go in the gutter 40–80 px above a row's cards, one y per line.
  - Merges go 30–60 px below a row's cards.
- **Flow maps:**
  - Row 1 runs from a start pill, which states the job ("When I have a free evening, I want…"), to an exit pill, "Job done: …".
  - Add rows only for branches that change whether the job gets done.
- **Checks** run on every render and fail on overlaps, decisions with fewer than 2 exits, gaps without IDs, and duplicate IDs. **Warnings** print for labels that overlap each other or sit on a node, and for a row that has nodes but no row label. Fix both.
- **The decisions panel** goes in the empty bottom-right: `P.panel('J2', x, y, w)`. It renders from `questions.json`. Add questions from the shell (`_uf.py add-question J2 "…"`), never in the spec, and answer them with the answer-questions skill.

## States of a gap
`todo` (NEEDS DESIGN) → `exploring` (EXPLORING, ROUND n) → `explored` (the chosen screen, EXPLORED · X) → `promoted`, or `later` (AFTER MVP) at any point. `found`: the library already had it; the card shows that frame ("DO4 · was N1·5"). State lives in `gaps.json`. Change it there and re-render the maps that show the gap.
