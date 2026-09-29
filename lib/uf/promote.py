"""Promotion: a confirmed exploration's screens become library frames.

Each screen of the chosen direction becomes its own artboard on the promote page (the library page), named with a
stable id, 'X1·1 · Google failed', exactly like every other library screen. The library index then includes them,
the master map places them in their area (instead of the gap's dashed frame), and the maps copy them.

    C = PromotedChapter(P, 1)          # prefix 'X' by default (config.json → promote_prefix)
    C.add('N1·3')                      # promoted gaps of this journey, in map order
    C.render(date)                     # → out/promoted_j1/promote.json and made/NN.html; nothing is written to the registry

After the frames are made: `_uf.py promoted promoted_j1 <node id>…` records ids and nodes in gaps.json.
"""
import importlib.util, json, os, sys
from . import base


def _load_spec(P, rel):
    path = os.path.join(P.root, rel)
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
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

    def render(self, *args):
        """render(date). The older render(story, date) still works; the story isn't used any more."""
        date = args[-1] if args else ''
        cid = f'{self.prefix}{self.J}'
        name = f'promoted_j{self.J}'
        # stable ids: keep what the registry already has, give new screens the next numbers
        used = [int(s.split('·')[1]) for _, g, _ in self.items for s in g.get('screen_ids', [])]
        nxt = max(used, default=0) + 1
        made = []
        for gid, g, d in self.items:
            ids = list(g.get('screen_ids', []))
            while len(ids) < len(d['screens']):
                ids.append(f'{cid}·{nxt}'); nxt += 1
            for sid, s in zip(ids, d['screens']):
                html = s['html']
                if 'layer-name="' in html[:html.index('>')]:          # the screen's root frame takes the stable id
                    head, rest = html.split('>', 1)
                    import re as _re
                    html = _re.sub(r'layer-name="[^"]*"', f'layer-name="{sid} · {s["label"]}"', head, 1) + '>' + rest
                made.append(dict(gap=gid, id=sid, name=f"{sid} · {s['label']}", width=base.PW, height=base.PH, html=html))
        out = os.path.join(self.P.root, 'out', name)
        md = os.path.join(out, 'made')
        os.makedirs(md, exist_ok=True)
        for f in os.listdir(md):
            os.remove(os.path.join(md, f))
        for j, m in enumerate(made):
            m['file'] = os.path.join(md, f'{j:02d}.html')
            open(m['file'], 'w').write(m['html'])
        page = self.P.cfg['sources']['paper'].get('promote_page') or self.P.cfg['sources']['paper'].get('library_page')
        plan = dict(board=name, chapter=cid, page=page, date=date, made=[{k: v for k, v in m.items() if k != 'html'} for m in made])
        json.dump(plan, open(os.path.join(out, 'promote.json'), 'w'), indent=1, ensure_ascii=False)
        print(f'{cid}: {len(made)} screens from {len(self.items)} gaps → page {page}')
        for m in made:
            print(f"  {m['name']} | {m['width']} x {m['height']} | {m['file']}")
        print(f'Make each as an artboard (create_artboard + write_html), then: _uf.py promoted {name} <node id of each, in this order>')
        return plan
