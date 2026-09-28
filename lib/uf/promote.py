"""Promoted chapter: confirmed exploration screens, laid out like a chapter on the screens page, with stable screen ids.
One chapter per journey: 'X2 · From explorations (Journey 2)', screens X2·1, X2·2, …
The screens are the exploration spec's own HTML for the chosen direction, so nothing is redrawn by hand."""
import importlib.util, os
from . import base, board
from .base import t, INK, MUTED, GREY

STEP = 470          # screen column pitch, like the confirmed chapters
TOP = 216


def _load_spec(P, rel):
    path = os.path.join(P.root, rel)
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, os.path.dirname(path))
    spec.loader.exec_module(mod)
    return mod.SPEC


class PromotedChapter:
    def __init__(self, project, journey_no, prefix=None):
        self.P = project
        self.J = journey_no
        self.prefix = prefix or project.cfg.get('promote_prefix', 'X')
        self.items = []

    def add(self, gid):
        """Adds every screen of the gap's chosen direction. The gap must be explored (confirmed)."""
        g = self.P.gap(gid)
        assert g.get('state') in ('explored', 'promoted'), f'{gid} is not confirmed yet'
        ex = [e for e in self.P.cfg['maps']['explorations'] if e['gap'] == gid]
        assert ex, f'{gid} has no exploration in config.json'
        SPEC = _load_spec(self.P, ex[0]['spec'])
        d = [d for r in SPEC['rounds'] for d in r['directions'] if d['letter'] == g['chosen']][0]
        self.items.append((gid, g, d))

    def render(self, story, date):
        cid = f'{self.prefix}{self.J}'
        B = board.Board(self.P, f'promoted_j{self.J}')
        # stable ids: reuse what the registry already has, give new screens the next numbers
        used = [int(s.split('·')[1]) for _, g, _ in self.items for s in g.get('screen_ids', [])]
        nxt = max(used, default=0) + 1
        cols = []
        for gid, g, d in self.items:
            ids = list(g.get('screen_ids', []))
            while len(ids) < len(d['screens']):
                ids.append(f'{cid}·{nxt}'); nxt += 1
            if ids != g.get('screen_ids'):
                self.P.set_gap(gid, screen_ids=ids, state='promoted', chapter=cid)
            for sid, s in zip(ids, d['screens']):
                cols.append((sid, gid, s))
        W = 40 + len(cols) * STEP + 40
        H = TOP + base.PH + 80
        B.add('header', f'<div layer-name="Header bar" style="position:absolute;left:40px;top:40px;width:{W-80}px;height:56px;background:{INK};border-radius:14px;display:flex;align-items:center;padding:0 20px;gap:16px;box-sizing:border-box">'
              + t(self.P.cfg.get('device_label', 'Mobile · iPhone'), 13, 18, 500, '#9AA4A6') + '<div style="width:1px;height:20px;background:#3A4245"></div>'
              + t(f'{cid} · From explorations (Journey {self.J})', 17, 22, 700, '#FFFFFF') + '<div style="flex:1"></div>'
              + t(f'Confirmed designs · {date}', 13, 18, 500, '#9AA4A6') + f'<div style="width:10px;height:10px;border-radius:5px;background:{base.ACCENT}"></div></div>')
        B.add('story', f'<div layer-name="Story line" style="position:absolute;left:40px;top:116px;width:{W-80}px">' + t(story, 17, 24, 500, MUTED) + '</div>')
        for i, (sid, gid, s) in enumerate(cols):
            x = 40 + i * STEP
            B.add('label' + sid.replace('·', '_'), f'<div layer-name="Step label" style="position:absolute;left:{x}px;top:176px;display:flex;gap:8px;align-items:baseline">'
                  + t(f'{sid} · {s["label"]}', 15, 20, 700, INK, 'white-space:nowrap;') + t(f'from {gid}', 13, 18, 500, GREY, 'white-space:nowrap;') + '</div>')
            html = s['html'].replace('position:relative;', f'position:absolute;left:{x}px;top:{TOP}px;', 1)
            B.add('screen' + sid.replace('·', '_'), html)
        print(f'{cid}: {len(cols)} screens from {len(self.items)} gaps')
        return B.emit(W, H, page='screens')
