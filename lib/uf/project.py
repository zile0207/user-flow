"""A project's user-flow folder: config, gap registry, paths. Created by the init skill.

<app repo>/design/user-flow/
  config.json      sources, theme, persona, maps (see references/project-layout.md)
  gaps.json        every needs-design gap: the single source of truth for ids, text and state
  ui_kit.py        the app's own screen parts, copied from its confirmed screens (for explorations)
  specs/           one file per map or exploration: master.py, j1.py, f1.py, explore_n2_1.py …
  img/  refs/      exported screen PNGs and reference images (gitignored, re-exportable)
  out/             rendered chunks (gitignored)
"""
import json, os, re
from . import base

HOME = os.path.join('design', 'user-flow')


def find(start):
    """Walk up from a file or folder to the nearest design/user-flow/config.json."""
    p = os.path.abspath(start)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    while True:
        for cand in (p, os.path.join(p, HOME)):
            if os.path.isfile(os.path.join(cand, 'config.json')) and os.path.basename(cand) == 'user-flow':
                return cand
        parent = os.path.dirname(p)
        if parent == p:
            raise FileNotFoundError('No design/user-flow/config.json above ' + start + '. Run the init skill first.')
        p = parent


class Project:
    def __init__(self, root):
        self.root = root
        self.cfg = json.load(open(os.path.join(root, 'config.json')))
        th = self.cfg.get('theme', {})
        base.set_theme(th.get('accent'), th.get('font'), tuple(th['device']) if th.get('device') else None)
        self.img_dir = os.path.join(root, 'img')
        self.refs_dir = os.path.join(root, 'refs')
        self.specs_dir = os.path.join(root, 'specs')
        for d in (self.img_dir, self.refs_dir, os.path.join(root, 'out')):
            os.makedirs(d, exist_ok=True)

    def out(self, name):
        return os.path.join(self.root, 'out', name)

    # ---------------- gap registry
    def _gaps_path(self):
        return os.path.join(self.root, 'gaps.json')

    def gaps(self):
        p = self._gaps_path()
        return json.load(open(p))['gaps'] if os.path.exists(p) else []

    def save_gaps(self, gaps):
        def key(g):
            m = re.match(r'N(\d+)·(\d+)', g['id'])
            return (int(m.group(1)), int(m.group(2))) if m else (999, 0)
        json.dump({'gaps': sorted(gaps, key=key)}, open(self._gaps_path(), 'w'), indent=2, ensure_ascii=False)

    def gap(self, gid):
        for g in self.gaps():
            if g['id'] == gid:
                return g
        raise KeyError(gid + ' is not in gaps.json')

    def next_gap_id(self, map_no):
        """Gap ids are N<map_no>·<n>, never renumbered: the next id is max + 1 for that map."""
        ns = [int(g['id'].split('·')[1]) for g in self.gaps() if g['id'].startswith(f'N{map_no}·')]
        return f'N{map_no}·{max(ns, default=0) + 1}'

    def add_gap(self, map_no, title, need, where=''):
        gid = self.next_gap_id(map_no)
        gs = self.gaps()
        gs.append({'id': gid, 'map': f'J{map_no}', 'title': title, 'need': need, 'where': where, 'state': 'todo'})
        self.save_gaps(gs)
        return gid

    def set_gap(self, gid, **fields):
        gs = self.gaps()
        for g in gs:
            if g['id'] == gid:
                g.update(fields)
        self.save_gaps(gs)

    def g(self, gid):
        """kwargs for Map.gap(...) straight from the registry, so maps never copy gap text by hand."""
        g = self.gap(gid)
        return dict(title=g['title'], need=g['need'], gid=gid, state=g.get('state', 'todo'),
                    chosen=g.get('chosen'), round=g.get('round'), img=g.get('img'))


def load(start=None):
    return Project(find(start or os.getcwd()))
