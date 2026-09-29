"""The master map as the library page itself, organised: no copies.

A master map that copies every screen doubles the file (a copy duplicates every layer, and Paper files have a
size limit). When the project has a library page, the master map is that page, laid out: every screen frame is
moved into its area, in the order the persona meets them, under a title band, with a dashed frame for each screen
still to design. Frames keep everything but their position. The page's other frames (section notes, bands) stay
where they are. Promoted screens (library frames made by promote-design) take their gap's place in its area.
Applying it is incremental: `_uf.py layout-ops` prints only the moves and frames that changed since the last
`_uf.py layout-commit`.

    L = LibraryLayout(P, cols=14, origin=(40000, 0))
    L.area('Onboarding', 'B1–B11', ['B'], gaps=['N1·1'], entries='first launch')
    L.render('Argo · every screen', 'Tue 29 Sep 2026')      → out/master/layout.json

layout.json holds: moves (library frames → left/top), and made (generated artboards: bands and gap frames, each
with its name, place, size and HTML). references/sync.md → "The organised library" says how to apply it.
"""
import json, os, re
from . import base
from .base import t, INK, MUTED, AMBER, LINE

GAP_X = 40            # between screens
LABEL = 120           # room above each row for Paper's artboard names
BAND_H = 260
AFTER_BAND = 80
AREA_GAP = 480
TALL_PITCH = 3200     # rows of frames whose height isn't known (full-page, fit-content)
PREFIX = 'master:'    # every generated artboard's name starts with this, so a re-layout can find and replace them


class LibraryLayout:
    def __init__(self, project, cols=10, origin=(40000, 0), per_row=4):
        """cols: screens across one area. per_row: areas side by side, left to right, then the next row."""
        self.P = project
        self.cols = cols
        self.per_row = per_row
        self.x0, self.y0 = origin
        self.areas = []
        lib = json.load(open(os.path.join(project.root, 'library.json')))
        self.screens = lib['screens']

    def area(self, name, sub, groups, gaps=(), entries='', match=None):
        nat = lambda x: [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', x['name'])]
        order = {g: i for i, g in enumerate(groups)}
        items = sorted((x for x in self.screens if x['group'] in groups and (not match or match in x['name'])),
                       key=lambda x: (order[x['group']], nat(x)))
        self.areas.append(dict(name=name, sub=sub, items=items, gaps=list(gaps), entries=entries))
        return len(items)

    # ---------------- generated frames
    def _band(self, a, w, n_screens, n_gaps):
        count = f'{n_screens} screens' + (f' · {n_gaps} to design' if n_gaps else '')
        return (f'<div layer-name="Band" style="width:{w}px;height:{BAND_H}px;background:#F1F3F3;border-radius:32px;padding:48px 56px;'
                f'display:flex;align-items:flex-end;justify-content:space-between;box-sizing:border-box">'
                '<div style="display:flex;flex-direction:column;gap:10px">'
                + t(a['name'], 88, 96, 700, INK, 'letter-spacing:-0.02em;white-space:nowrap;')
                + t(a['sub'] + (f' · entry points: {a["entries"]}' if a['entries'] else ''), 32, 40, 500, MUTED, 'white-space:nowrap;') + '</div>'
                + t(count, 36, 44, 700, AMBER if n_gaps else MUTED, 'white-space:nowrap;') + '</div>')

    def _gap(self, g):
        st = g.get('state', 'todo')
        tag = {'later': 'AFTER MVP', 'exploring': f"EXPLORING · ROUND {g.get('round') or 1}",
               'explored': f"EXPLORED · {g.get('chosen')} · on the Exploration page"}.get(st, 'NEEDS DESIGN')
        col = '#6B7678' if st == 'later' else (base.ACCENT if st == 'explored' else AMBER)
        return (f'<div layer-name="Gap" style="width:{base.PW}px;height:{base.PH}px;background:#FBFBFA;border:3px dashed #B4BDBF;border-radius:40px;'
                f'padding:40px 32px;display:flex;flex-direction:column;justify-content:center;gap:20px;box-sizing:border-box">'
                + t(f"{g['id']} · {tag}", 18, 24, 700, col, 'letter-spacing:0.06em;')
                + t(g['title'], 34, 40, 700, INK, 'letter-spacing:-0.01em;') + t(g['need'], 20, 28, 500, MUTED) + '</div>')

    # ---------------- layout
    def _place_area(self, a, x0, y0, W, moves, made):
        """Lays one area out at (x0, y0). Returns its height."""
        allg = [self.P.gap(g) for g in a['gaps']]
        gaps = [g for g in allg if g.get('state', 'todo') in ('todo', 'exploring', 'later', 'explored')]
        promoted = [dict(node=n, name=f'{sid} (was {g["id"]})') for g in allg if g.get('state') == 'promoted'
                    for sid, n in zip(g.get('screen_ids', []), g.get('screen_nodes', []))]
        n_todo = sum(1 for g in gaps if g.get('state', 'todo') in ('todo', 'exploring'))
        key = ''.join(ch for ch in a['name'].title() if ch.isalnum())
        made.append(dict(name=f'{PREFIX}band{key} · {a["name"]}', left=x0, top=y0, width=W, height=BAND_H,
                         html=self._band(a, W, len(a['items']), n_todo)))
        y = y0 + BAND_H + AFTER_BAND + LABEL
        fixed = [s for s in a['items'] if s.get('h') not in ('?', None)] + promoted     # promoted frames replace their gap
        tall = [s for s in a['items'] if s.get('h') in ('?', None)]
        cells = [('screen', s) for s in fixed] + [('gap', g) for g in gaps]
        for rows, pitch in ((cells, base.PH + LABEL + GAP_X), ([('screen', s) for s in tall], TALL_PITCH)):
            for i, (kind, it) in enumerate(rows):
                x = x0 + (i % self.cols) * (base.PW + GAP_X)
                yy = y + (i // self.cols) * pitch
                if kind == 'screen':
                    moves.append(dict(node=it['node'], name=it['name'], left=x, top=yy))
                else:
                    made.append(dict(name=f'{PREFIX}gap · {it["id"]} · {it["title"]}', left=x, top=yy, width=base.PW, height=base.PH, html=self._gap(it)))
            if rows:
                y += ((len(rows) - 1) // self.cols + 1) * pitch
        return y - y0

    def render(self, title, date, name='master', to_page=None):
        """to_page: lay the frames out on another page (they move there, ids intact), which then becomes the library."""
        W = self.cols * base.PW + (self.cols - 1) * GAP_X
        total_w = self.per_row * W + (self.per_row - 1) * AREA_GAP
        moves, made = [], []
        made.append(dict(name=f'{PREFIX}title · {title}', left=self.x0, top=self.y0, width=total_w, height=BAND_H,
                         html=(f'<div layer-name="Title" style="width:{total_w}px;height:{BAND_H}px;background:{INK};border-radius:32px;padding:48px 56px;'
                               f'display:flex;align-items:flex-end;justify-content:space-between;box-sizing:border-box">'
                               + t(title, 96, 104, 700, '#FFFFFF', 'letter-spacing:-0.02em;white-space:nowrap;')
                               + t(f'The master map: every confirmed screen, by area, in the order {self.P.cfg.get("persona", {}).get("name", "the persona")} meets them · {date}',
                                   32, 40, 500, '#9AA4A6', 'white-space:nowrap;') + '</div>')))
        y = self.y0 + BAND_H + AREA_GAP
        for r in range(0, len(self.areas), self.per_row):
            heights = [self._place_area(a, self.x0 + c * (W + AREA_GAP), y, W, moves, made)
                       for c, a in enumerate(self.areas[r:r + self.per_row])]
            y += max(heights) + AREA_GAP
        W = total_w
        placed = {m['node'] for m in moves}
        left_out = [s['name'] for s in self.screens if s['node'] not in placed]
        out = os.path.join(self.P.root, 'out', name)
        os.makedirs(out, exist_ok=True)
        src = self.P.cfg['sources']['paper'].get('library_page')
        import hashlib
        for m in made:
            m['h'] = hashlib.sha1(m['html'].encode()).hexdigest()[:12]
        plan = dict(board=name, page=to_page or src, from_page=src, prefix=PREFIX, moves=moves, made=made,
                    left_out=left_out, size=[W, y - self.y0])
        json.dump(plan, open(os.path.join(out, 'layout.json'), 'w'), indent=1, ensure_ascii=False)
        print(f'{name}: {len(moves)} library frames to move · {len(made)} frames to make ({len(self.areas)} bands, '
              f'{len(made) - len(self.areas) - 1} gaps) · {W} x {y - self.y0} at ({self.x0}, {self.y0})')
        if left_out:
            print(f'  not in any area: {len(left_out)} · ' + ', '.join(left_out[:8]))
        return plan
