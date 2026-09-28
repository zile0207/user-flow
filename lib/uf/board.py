"""Boards as keyed elements, so a board can be synced instead of repainted.

Every top-level element on a board gets a stable key, stamped at the front of its layer name:
    layer-name="j2:g_share · N2·1 · Share to Argo"
A render writes:
    out/<board>/full/NN.html     everything, for a first paint (chunks of about CHUNK_MAX chars)
    out/<board>/manifest.json    key → hash of every element, in paint order
    out/<board>/sync/plan.json   what changed since the last commit: insert · replace · delete
The last painted state lives in boards/<board>.json (committed), written by `--commit <artboard id>`.

Spec command line (every spec calls Board.emit, which reads these):
    python3 specs/j2.py                       render, write full chunks and the sync plan
    python3 specs/j2.py --drift <children.json>   compare with the live board (get_children output) → ops with node ids
    python3 specs/j2.py --commit <artboard id>    record what is now on the board
"""
import hashlib, json, os, sys
from . import base

VERSION = '0.2.0'
CHUNK_MAX = 12000


def h(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]


class Board:
    def __init__(self, project, name):
        self.P = project
        self.name = name
        self.keys = []
        self.html = {}

    def add(self, key, html):
        assert ' · ' not in key and ':' not in key, f'bad key {key}'
        if key in self.html:
            n = 2
            while f'{key}.{n}' in self.html:
                n += 1
            key = f'{key}.{n}'
        head = html[:html.index('>')]
        assert 'layer-name="' in head, f'element {key} has no layer-name on its root tag'
        self.html[key] = html.replace('layer-name="', f'layer-name="{self.name}:{key} · ', 1)
        self.keys.append(key)
        return key

    # ---------------- output
    def _dir(self, *p):
        d = os.path.join(self.P.root, 'out', self.name, *p)
        os.makedirs(d, exist_ok=True)
        return d

    def _state_path(self):
        d = os.path.join(self.P.root, 'boards')
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, f'{self.name}.json')

    def emit(self, W, H, page='maps'):
        full = self._dir('full'); sync = self._dir('sync')
        for d in (full, sync):
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
        # full paint, in order, chunked
        chunks, cur = [], ''
        for k in self.keys:
            if cur and len(cur) + len(self.html[k]) > CHUNK_MAX:
                chunks.append(cur); cur = ''
            cur += self.html[k]
        if cur:
            chunks.append(cur)
        for i, c in enumerate(chunks):
            open(os.path.join(full, f'{i:02d}.html'), 'w').write(c)
        root = self.P.root
        manifest = {'board': self.name, 'version': VERSION, 'size': [W, H], 'page': page,
                    'elements': [[k, h(self.html[k].replace(root, '@'))] for k in self.keys]}   # path-independent
        json.dump(manifest, open(os.path.join(self._dir(), 'manifest.json'), 'w'), indent=1)

        prev = json.load(open(self._state_path())) if os.path.exists(self._state_path()) else None
        pinned = self.P.cfg.get('plugin_version')
        if pinned and pinned != VERSION:
            print(f'  note: this project was set up with user-flow {pinned}; rendering with {VERSION}. Unchanged specs may still re-render differently.')
        plan = self._plan(prev, manifest, sync)
        print(f'{self.name}: {len(self.keys)} elements · {len(chunks)} full chunks · artboard {W} x {H}')
        if plan['mode'] == 'full':
            print(f'  sync: no committed state yet → paint in full (out/{self.name}/full)')
        else:
            c = plan['counts']
            print(f"  sync: {c['insert']} insert · {c['replace']} replace · {c['delete']} delete"
                  + (f" · renderer {prev.get('version')} → {VERSION}" if prev.get('version') != VERSION else ''))
        self._cli(manifest, prev)
        return plan

    def _plan(self, prev, manifest, sync):
        if not prev or not prev.get('elements'):
            plan = {'mode': 'full', 'artboard': prev.get('artboard') if prev else None}
        else:
            old = dict(prev['elements']); new = dict(manifest['elements'])
            ops = []
            for k in old:
                if k not in new:
                    ops.append({'op': 'delete', 'key': k})
            for i, (k, hh) in enumerate(manifest['elements']):
                if k not in old:
                    f = f'ins_{i:03d}.html'; open(os.path.join(sync, f), 'w').write(self.html[k])
                    ops.append({'op': 'insert', 'key': k, 'file': f})
                elif old[k] != hh:
                    f = f'rep_{i:03d}.html'; open(os.path.join(sync, f), 'w').write(self.html[k])
                    ops.append({'op': 'replace', 'key': k, 'file': f})
            counts = {o: sum(1 for x in ops if x['op'] == o) for o in ('insert', 'replace', 'delete')}
            plan = {'mode': 'sync', 'artboard': prev.get('artboard'), 'ops': ops, 'counts': counts,
                    'size_changed': prev.get('size') != manifest['size'], 'size': manifest['size']}
        json.dump(plan, open(os.path.join(sync, 'plan.json'), 'w'), indent=1)
        return plan

    # ---------------- command line
    def _cli(self, manifest, prev):
        a = sys.argv
        if '--drift' in a:
            self._drift(a[a.index('--drift') + 1], prev)
        if '--commit' in a:
            art = a[a.index('--commit') + 1]
            state = dict(manifest, artboard=art)
            json.dump(state, open(self._state_path(), 'w'), indent=1)
            print(f'  committed: boards/{self.name}.json now matches artboard {art}')

    def _drift(self, children_file, prev):
        """children_file: the JSON from get_children(artboard) (the whole result, or its 'children' list)."""
        data = json.load(open(children_file))
        kids = data.get('children', data) if isinstance(data, dict) else data
        pre = f'{self.name}:'
        live = {}
        unkeyed = []
        for c in kids:
            nm = c['name']
            if nm.startswith(pre):
                live[nm[len(pre):].split(' · ')[0]] = c['id']
            else:
                unkeyed.append(nm)
        known = dict(prev['elements']) if prev and prev.get('elements') else {}
        missing = [k for k in known if k not in live]
        extra_keys = [k for k in live if k not in known]
        plan_path = os.path.join(self._dir('sync'), 'plan.json')
        plan = json.load(open(plan_path))
        if plan['mode'] == 'sync':
            for op in plan['ops']:
                if op['op'] in ('replace', 'delete'):
                    op['node'] = live.get(op['key'])
            json.dump(plan, open(plan_path, 'w'), indent=1)
        print(f'  drift: {len(live)} keyed on the board · {len(unkeyed)} unkeyed (hand-made or pre-sync) · '
              f'{len(missing)} missing (deleted by hand) · {len(extra_keys)} unknown keys')
        for n in unkeyed[:10]:
            print('    unkeyed:', n)
        for k in missing[:10]:
            print('    missing:', k)
        if plan['mode'] == 'sync' and any(op.get('node') is None for op in plan['ops'] if op['op'] != 'insert'):
            print('  warning: some replace/delete targets are not on the board; paint in full instead')
