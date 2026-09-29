"""Boards as keyed elements, so a board can be synced instead of repainted.

Every top-level element on a board gets a stable key, stamped at the front of its layer name:
    layer-name="j2:g_share · N2·1 · Share to Argo"
A render writes:
    out/<board>/full/NN.html     everything, for a first paint (chunks of about CHUNK_MAX chars)
    out/<board>/manifest.json    per element: key, hash, hash without position, left, top
    out/<board>/sync/plan.json   what changed since the last commit: delete · rename · replace · move · insert
The last painted state lives in boards/<board>.json (committed), written by `--commit <artboard id>`.

Spec command line (every spec calls Board.emit, which reads these):
    python3 specs/j2.py                          render, write full chunks and the sync plan
    python3 specs/j2.py --drift <tree file>      compare with the live board → node ids in the plan, plus hand edits
    python3 specs/j2.py --commit <artboard id>   record what is now on the board

<tree file> is get_tree_summary(artboard, depth 1) saved as text (or its JSON result), a get_children JSON
result, or plain lines "<node id> <layer name>". get_children stops at 100 children: don't use it for big boards.
"""
import hashlib, json, os, re, sys
from . import base

VERSION = '0.4.0'
CHUNK_MAX = 12000
CLONE_MAX = 6          # live screen copies per paste chunk: each one returns a very large write_html response
NAME_MAX = 50          # Paper truncates layer names here; keys must survive it


def h(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]


_LEFT = re.compile(r'(?<![-\w])left:\s*(-?[\d.]+)px')
_TOP = re.compile(r'(?<![-\w])top:\s*(-?[\d.]+)px')


def _num(s):
    f = float(s)
    return int(f) if f == int(f) else f


def _num_fmt(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else f'{v:g}'


def scale_html(html, s):
    """Draw an element s times larger: every px value, every svg's width and height (its viewBox stays, so its
    drawing scales too) and every zoom. A zoom that comes out at 1 is dropped: the frame shows at its real size."""
    from .base import NOSCALE
    if NOSCALE[0] in html:                   # real frames inside keep their real size
        parts = re.split('(' + re.escape(NOSCALE[0]) + '.*?' + re.escape(NOSCALE[1]) + ')', html, flags=re.S)
        return ''.join(p[len(NOSCALE[0]):-len(NOSCALE[1])] if p.startswith(NOSCALE[0]) else scale_html(p, s) for p in parts)
    if s == 1:
        return html
    out = re.sub(r'(-?\d+(?:\.\d+)?)px', lambda m: _num_fmt(float(m.group(1)) * s) + 'px', html)
    def svg_tag(m):
        return re.sub(r'\s(width|height)="([\d.]+)"', lambda a: f' {a.group(1)}="{_num_fmt(float(a.group(2)) * s)}"', m.group(0))
    out = re.sub(r'<svg\b[^>]*>', svg_tag, out)

    def z(m):
        v = float(m.group(1)) * s
        return '' if abs(v - 1) < 0.01 else f';zoom:{_num_fmt(v)}'
    return re.sub(r';zoom:([\d.]+)', z, out)


def tree_data(raw):
    """A tree summary as text, or a get_children result as data, from whatever was saved: the plain summary, the tool's
    JSON result, or the JSON file a harness saves a large tool result to ([{"type": "text", "text": …}])."""
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    if isinstance(data, list) and data and isinstance(data[0], dict) and 'text' in data[0]:
        raw = '\n'.join(x.get('text', '') for x in data)
        data = None
    if isinstance(data, dict) and 'summary' in data:
        return data['summary']
    if isinstance(data, (dict, list)):
        return data
    m = re.search(r'"summary":\s*"((?:[^"\\]|\\.)*)"', raw)
    if m:
        return json.loads('"' + m.group(1) + '"')
    return raw


def position(html):
    """(left, top) of the element's root tag, or None when it isn't absolutely placed."""
    head = html[:html.index('>')]
    l, t_ = _LEFT.search(head), _TOP.search(head)
    return (_num(l.group(1)), _num(t_.group(1))) if l and t_ else None


def _unplaced(html):
    head, rest = html[:html.index('>')], html[html.index('>'):]
    return _TOP.sub('top:@', _LEFT.sub('left:@', head, 1), 1) + rest


class Board:
    def __init__(self, project, name, scale=1):
        """scale: draw the whole board this much larger than its spec (a map is scaled so its screens are real size)."""
        self.P = project
        self.name = name
        self.scale = scale
        self.keys = []
        self.html = {}       # stamped, as painted
        self.body = {}       # unstamped, for hashing

    def add(self, key, html):
        assert ' · ' not in key and ':' not in key, f'bad key {key}'
        key = re.sub(r'[^\w.]', '_', key)
        if len(f'{self.name}:{key} · ') > NAME_MAX - 8:          # keep the key readable after Paper's 50-char cut
            key = key[:20] + '_' + h(key)[:6]
        if key in self.html:
            n = 2
            while f'{key}.{n}' in self.html:
                n += 1
            key = f'{key}.{n}'
        head = html[:html.index('>')]
        assert 'layer-name="' in head, f'element {key} has no layer-name on its root tag'
        html = scale_html(html, self.scale)
        self.body[key] = html
        self.html[key] = self._stamp(html, key)
        self.keys.append(key)
        return key

    def _stamp(self, html, key):
        return html.replace('layer-name="', f'layer-name="{self.name}:{key} · ', 1)

    def _layer_name(self, key):
        s = self.html[key]
        i = s.index('layer-name="') + len('layer-name="')
        return s[i:s.index('"', i)]

    # ---------------- output
    def _dir(self, *p):
        d = os.path.join(self.P.root, 'out', self.name, *p)
        os.makedirs(d, exist_ok=True)
        return d

    def _state_path(self):
        d = os.path.join(self.P.root, 'boards')
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, f'{self.name}.json')

    def _rel(self, s):
        return s.replace(self.P.root, '@')      # hashes must not depend on where the repo lives

    def _chunks(self, keys):
        chunks, cur = [], ''
        for k in keys:
            html = self.html[k]
            if cur and (len(cur) + len(html) > CHUNK_MAX
                        or cur.count('<x-paper-clone') + html.count('<x-paper-clone') > CLONE_MAX):
                chunks.append(cur); cur = ''
            cur += html
        if cur:
            chunks.append(cur)
        return chunks

    def clones(self):
        """key → the Paper frames each element copies (for `_uf.py stale`)."""
        return {k: re.findall(r'<x-paper-clone node-id="([^"]+)"', self.html[k]) for k in self.keys if '<x-paper-clone' in self.html[k]}

    def emit(self, W, H, page='maps'):
        W, H = round(W * self.scale), round(H * self.scale)
        for f in ('local_needed.json', 'frames_needed.txt'):
            if os.path.exists(os.path.join(self._dir(), f)):
                os.remove(os.path.join(self._dir(), f))
        if base.LOCAL_NEEDED:
            json.dump({k: list(v) for k, v in base.LOCAL_NEEDED.items()}, open(os.path.join(self._dir(), 'local_needed.json'), 'w'), indent=1)
            print(f'  {len(base.LOCAL_NEEDED)} screens are not on the Frames page yet (they show as markers): `_uf.py frames-local {self.name}`')
        if base.MISSING:
            need = os.path.join(self._dir(), 'frames_needed.txt')
            open(need, 'w').write(''.join(f'{n}\n' for n in sorted(base.MISSING)))
            print(f'  {len(base.MISSING)} frames not fetched yet (they show as markers): `_uf.py frames {self.name}`')
        full = self._dir('full'); sync = self._dir('sync')
        for d in (full, sync):
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
        # Elements that show a screen go first, in chunks that can be pasted in parallel (they never overlap each
        # other); everything else (arrows, labels, panels) follows in order, so it sits on top.
        screens = [k for k in self.keys if 'layer-name="Screen"' in self.html[k]]
        rest = [k for k in self.keys if k not in screens]
        par, ser = self._chunks(screens), self._chunks(rest)
        chunks = par + ser
        for i, c in enumerate(chunks):
            open(os.path.join(full, f'{i:02d}.html'), 'w').write(c)
        json.dump({'parallel': [f'{i:02d}.html' for i in range(len(par))],
                   'serial': [f'{i:02d}.html' for i in range(len(par), len(chunks))]},
                  open(os.path.join(full, 'paint.json'), 'w'), indent=1)
        els = []
        for k in self.keys:
            b = self._rel(self.body[k]); pos = position(b)
            els.append([k, h(b), h(_unplaced(b)) if pos else h(b), pos[0] if pos else None, pos[1] if pos else None])
        manifest = {'board': self.name, 'version': VERSION, 'format': 2, 'size': [W, H], 'page': page, 'elements': els}
        json.dump(manifest, open(os.path.join(self._dir(), 'manifest.json'), 'w'), indent=1)
        json.dump(self.clones(), open(os.path.join(self._dir(), 'clones.json'), 'w'), indent=1)

        prev = json.load(open(self._state_path())) if os.path.exists(self._state_path()) else None
        pinned = self.P.cfg.get('plugin_version')
        if pinned and pinned != VERSION:
            print(f'  note: this project was set up with user-flow {pinned}; rendering with {VERSION}. '
                  'Unchanged specs may still re-render differently. Update config.json → plugin_version after the next sync.')
        plan = self._plan(prev, manifest, sync)
        committing = '--commit' in sys.argv
        print(f'{self.name}: {len(self.keys)} elements · {len(chunks)} full chunks · artboard {W} x {H}')
        if not committing:
            if plan['mode'] == 'full':
                print(f'  sync: no committed state yet → paint in full (out/{self.name}/full)')
            else:
                c = plan['counts']
                print(f"  sync: {c['insert']} insert · {c['replace']} replace · {c['move']} move · {c['rename']} rename · {c['delete']} delete"
                      + (' · artboard size changed' if plan['size_changed'] else '')
                      + (f" · renderer {prev.get('version')} → {VERSION}" if prev.get('version') != VERSION else ''))
        self._cli(manifest, prev)
        return plan

    # ---------------- the plan
    def _legacy_hash(self, key, as_key=None):
        """How format 1 (0.2.x) hashed an element: the stamped html, key included."""
        return h(self._rel(self._stamp(self.body[key], as_key or key)))

    def _plan(self, prev, manifest, sync):
        if not prev or not prev.get('elements'):
            plan = {'mode': 'full', 'artboard': prev.get('artboard') if prev else None}
            json.dump(plan, open(os.path.join(sync, 'plan.json'), 'w'), indent=1)
            return plan
        old = {e[0]: e for e in prev['elements']}
        new = {e[0]: e for e in manifest['elements']}
        legacy = prev.get('format', 1) < 2

        def same(k):            # nothing to do
            return old[k][1] == (self._legacy_hash(k) if legacy else new[k][1])

        gone = [k for k in old if k not in new]
        fresh = [k for k in new if k not in old]
        renames = {}             # new key → old key, for elements whose key changed but nothing else did
        by_hash = {}
        for k in gone:
            by_hash.setdefault(old[k][1], []).append(k)
        for k in fresh:
            if legacy:
                hit = next((o for o in gone if o not in renames.values() and old[o][1] == self._legacy_hash(k, o)), None)
            else:
                hit = next((o for o in by_hash.get(new[k][1], []) if o not in renames.values()), None)
            if hit:
                renames[k] = hit

        ops = []
        for k in gone:
            if k not in renames.values():
                ops.append({'op': 'delete', 'key': k})
        for k, o in renames.items():
            ops.append({'op': 'rename', 'key': o, 'to': k, 'name': self._layer_name(k)})
        inserts = []
        for i, k in enumerate(self.keys):
            e = new[k]
            if k in renames:
                continue
            if k not in old:
                inserts.append(k)
            elif same(k):
                continue
            elif not legacy and old[k][2] == e[2] and e[3] is not None:
                ops.append({'op': 'move', 'key': k, 'left': e[3], 'top': e[4]})
            else:
                f = f'rep_{i:03d}.html'; open(os.path.join(sync, f), 'w').write(self.html[k])
                op = {'op': 'replace', 'key': k, 'file': f}
                if e[3] is not None:
                    op.update(left=e[3], top=e[4])     # write_html(replace) keeps the old node's place: set it after
                ops.append(op)
        for j, c in enumerate(self._chunks(inserts)):
            f = f'ins_{j:02d}.html'; open(os.path.join(sync, f), 'w').write(c)
            ops.append({'op': 'insert', 'keys': [k for k in inserts if self.html[k] in c], 'file': f})
        counts = {o: sum(1 for x in ops if x['op'] == o) for o in ('delete', 'rename', 'replace', 'move')}
        counts['insert'] = len(inserts)
        plan = {'mode': 'sync', 'artboard': prev.get('artboard'), 'ops': ops, 'counts': counts,
                'size_changed': prev.get('size') != manifest['size'], 'size': manifest['size']}
        json.dump(plan, open(os.path.join(sync, 'plan.json'), 'w'), indent=1)
        return plan

    # ---------------- command line
    def _cli(self, manifest, prev):
        a = sys.argv
        if '--drift' in a:
            self._drift(a[a.index('--drift') + 1], prev, manifest)
        if '--commit' in a:
            art = a[a.index('--commit') + 1]
            state = dict(manifest, artboard=art)
            json.dump(state, open(self._state_path(), 'w'), indent=1)
            print(f'  committed: boards/{self.name}.json now matches artboard {art}')

    @staticmethod
    def read_tree(path):
        """[(node id, layer name)] of the artboard's direct children, from any of the accepted formats."""
        raw = open(path).read()
        data = tree_data(raw)
        if isinstance(data, str):
            rows = []
            for line in data.splitlines():
                m = re.match(r'^ {2}\S+ "(.*)" \(([\w]+-[\w]+)\)', line)            # get_tree_summary, depth 1
                if m:
                    rows.append((m.group(2), m.group(1))); continue
                m = re.match(r'^\s*([0-9A-Z]+-[0-9A-Z]+)\s+(.+?)\s*$', line)         # "<node id> <layer name>"
                if m:
                    rows.append((m.group(1), m.group(2)))
            return rows, False
        kids = data.get('children', data) if isinstance(data, dict) else data
        truncated = (isinstance(data, dict) and any(data.get(k) for k in ('truncated', 'hasMore'))) or len(kids) == 100
        return [(c['id'], c['name']) for c in kids], truncated

    def _drift(self, tree_file, prev, manifest):
        rows, truncated = self.read_tree(tree_file)
        if truncated:
            print('  drift: this looks like a get_children result cut at 100 children. '
                  'Use get_tree_summary(artboard, depth 1) instead; nothing was changed.')
            sys.exit(2)
        pre = f'{self.name}:'
        live, unkeyed = {}, []
        for nid, nm in rows:
            if nm.startswith(pre):
                live[nm[len(pre):].split(' · ')[0].strip()] = nid
            else:
                unkeyed.append((nid, nm))
        known = [e[0] for e in prev['elements']] if prev and prev.get('elements') else []
        missing = [k for k in known if k not in live]
        extra_keys = [k for k in live if k not in known]
        plan_path = os.path.join(self._dir('sync'), 'plan.json')
        plan = json.load(open(plan_path))
        if plan['mode'] == 'sync':
            for op in plan['ops']:
                if op['op'] != 'insert':
                    op['node'] = live.get(op['key'])
            plan['unkeyed'] = [nid for nid, _ in unkeyed]
            json.dump(plan, open(plan_path, 'w'), indent=1)
        print(f'  drift: {len(live)} keyed on the board · {len(unkeyed)} unkeyed (added by hand) · '
              f'{len(missing)} missing (deleted by hand) · {len(extra_keys)} unknown keys')
        for nid, nm in unkeyed[:20]:
            print(f'    unkeyed: {nid} {nm}')
        for k in missing[:20]:
            print('    missing:', k)
        print('  drift can\'t see edits inside an element (text, colour, position). Ask if the board was edited by hand.')
        if plan['mode'] == 'sync' and any(op.get('node') is None for op in plan['ops'] if op['op'] != 'insert'):
            print('  warning: some targets are not on the board; paint in full instead')
