"""The library: a page that holds every confirmed screen of the app, however it is organised.

Journeys put these screens in context. Before anything becomes a needs-design gap, look for it here.
`design/user-flow/library.json` indexes the page, built from its tree summary:

    get_tree_summary(root_node_<library page>, depth 1)  →  out/library_tree.txt
    python3 design/user-flow/specs/_uf.py library out/library_tree.txt

A frame as wide as the device is a screen; wider or much shorter frames are section headers and bands.
"""
import json, os, re

STOP = set('a an and the of to in on at is it its for with from by or no not your you my one this that then be after before '
           'page half widget decided'.split())


def _words(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1]


def _group(head):
    """The family a screen belongs to: '5.4' stays '5.4', 'DO10' → 'DO', 'MON b' → 'MON', 'N1b' → 'N', 'GATE a' → 'GATE'."""
    tok = head.split()[0] if head.split() else head
    m = re.match(r'^([A-Z]+)\d+[a-z]?$', tok)
    return m.group(1) if m else tok


def ref_of(name):
    """A short screen id from a frame name: '5.4 · 7 · The video is private' → '5.4·7', 'DO4 · …' → 'DO4', 'MON b · Page' → 'MON b'."""
    parts = [p.strip() for p in re.split(r' · | — ', name) if p.strip()]
    if len(parts) > 1 and re.match(r'^\d+(\.\d+)?[a-z]?$', parts[0]) and re.match(r'^([A-Z]?\d+[a-z]?|[A-Z])$', parts[1]):
        return f'{parts[0]}·{parts[1]}'
    return parts[0] if parts else name


def parse(text, device_w=390):
    from .board import tree_data
    text = tree_data(text)
    screens, headers = [], []
    for line in text.splitlines():
        m = re.match(r'^ {2}\S+ "(.*)" \(([\w]+-[\w]+)\) (\S+)×(\S+)', line)
        if not m:
            continue
        name, node, w, h = m.groups()
        if name.startswith('master:'):          # the plugin's own layout frames (bands, gap frames), not screens
            continue
        parts = [p.strip() for p in re.split(r' · | — ', name) if p.strip()]
        group = _group(parts[0] if parts else name)
        entry = {'node': node, 'name': name, 'ref': ref_of(name), 'group': group, 'title': ' · '.join(parts[1:]) or name, 'w': w, 'h': h}
        try:
            is_screen = float(w) == device_w and (h == '?' or float(h) > 400)
        except ValueError:
            is_screen = False
        (screens if is_screen else headers).append(entry)
    return screens, headers


class Library:
    def __init__(self, P):
        self.P = P
        self.path = os.path.join(P.root, 'library.json')
        self.data = json.load(open(self.path)) if os.path.exists(self.path) else None

    def build(self, tree_file):
        paper = self.P.cfg.get('sources', {}).get('paper', {})
        dw = (self.P.cfg.get('theme', {}).get('device') or [390])[0]
        screens, headers = parse(open(tree_file).read(), dw)
        self.data = {'page': paper.get('library_page'), 'page_name': paper.get('library_page_name'),
                     'screens': screens, 'headers': headers}
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=1, ensure_ascii=False)
            f.write('\n')
        return len(screens), len(headers)

    def screens(self):
        return (self.data or {}).get('screens', [])

    def find(self, query, limit=12):
        """Screens whose name shares the most words with the query. The agent confirms each hit with a screenshot."""
        q = set(_words(query))
        scored = []
        for s in self.screens():
            words = _words(s['name'])
            hit = q & set(words)
            if hit:
                scored.append((len(hit) / (len(q) ** 0.5 * max(1, len(set(words))) ** 0.5), sorted(hit), s))
        scored.sort(key=lambda x: -x[0])
        return scored[:limit]

    def used_on(self, board):
        """Image names (node ids without -0) a rendered board already shows."""
        d = os.path.join(self.P.root, 'out', board, 'full')
        html = ''.join(open(os.path.join(d, f)).read() for f in sorted(os.listdir(d))) if os.path.isdir(d) else ''
        return set(re.findall(r'/img/([^/"]+)\.png', html))

    def unplaced(self, board, groups):
        used = self.used_on(board)
        return [s for s in self.screens() if s['group'] in groups and s['node'].replace('-0', '') not in used]
