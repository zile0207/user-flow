"""Bind a library frame's literal values to the project's design tokens.

The token file (config.json → sources.paper.tokens.source) lists tokens the way Paper's create_tokens takes them
({type, name, value}) and may add:
    snap:  {kind: {literal: css value}}   near-duplicates, snapped to a token (or a color-mix of one)
    keep:  {kind: [values]}               values that stay literal on purpose (system UI, other companies' marks)

A frame is read with two calls, both cheap and uncapped (find_nodes stops at 200 nodes and can't see SVG colours):
    get_jsx(nodeId, format "inline-styles")   every layer's styles, SVG strokes and fills included, in document order
    get_tree_summary(nodeId, depth 30)        every layer's node id, in the same order
pair() walks both together, so each JSX element gets its node id. plan() turns the frames into update_styles
payloads: every node that needs the same change goes into one entry, across all the frames in the batch.
"""
import json, os, re

COLOR = ['backgroundColor', 'color', 'borderColor', 'borderTopColor', 'borderBottomColor', 'borderLeftColor',
         'borderRightColor', 'outlineColor', 'textDecorationColor', 'fill', 'stroke', 'stopColor']
RADIUS = ['borderRadius', 'borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomLeftRadius',
          'borderBottomRightRadius']
SPACING = ['gap', 'rowGap', 'columnGap', 'padding', 'paddingInline', 'paddingBlock', 'paddingTop', 'paddingBottom',
           'paddingLeft', 'paddingRight']
MARGIN = ['margin', 'marginTop', 'marginBottom', 'marginLeft', 'marginRight', 'marginInline', 'marginBlock']
KIND = {**{p: 'color' for p in COLOR}, **{p: 'radius' for p in RADIUS}, **{p: 'spacing' for p in SPACING},
        **{p: 'margin' for p in MARGIN},
        'fontSize': 'fontSize', 'lineHeight': 'lineHeight', 'fontWeight': 'fontWeight',
        'letterSpacing': 'letterSpacing', 'fontFamily': 'fontFamily', 'opacity': 'opacity'}
SVG_ATTR = {'fill': 'fill', 'stroke': 'stroke', 'stop-color': 'stopColor', 'stopColor': 'stopColor'}
FACES = {'thin': 100, 'extralight': 200, 'light': 300, 'regular': 400, 'book': 400, 'medium': 500, 'semibold': 600,
         'bold': 700, 'extrabold': 800, 'black': 900}
BOUND = ('var(', 'color-mix(')
TEXT_ONLY = ('fontSize', 'lineHeight', 'fontWeight', 'fontFamily', 'letterSpacing')


def _px(v):
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)(px)?', str(v).strip())
    return float(m.group(1)) if m else None


def _hex(v):
    """'#fff', '#FFFFFF80', 'rgb(…)', 'rgba(…)' → '#RRGGBB' or '#RRGGBBAA' (upper case), else None."""
    v = str(v).strip()
    m = re.fullmatch(r'#([0-9a-fA-F]{3,8})', v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = ''.join(c * 2 for c in h)
        return '#' + h.upper() if len(h) in (6, 8) else None
    m = re.fullmatch(r'rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)', v)
    if m:
        r, g, b, a = m.groups()
        out = '#%02X%02X%02X' % (int(r), int(g), int(b))
        if a is not None:
            a = float(a[:-1]) / 100 if a.endswith('%') else float(a)
            if a < 1:
                out += '%02X' % round(a * 255)
        return out
    return None


def _num(v):
    return f'{float(v):g}'


class Tokens:
    def __init__(self, path):
        d = json.load(open(path))
        self.path = path
        self.by = {}                       # kind → {normalised value → css value}
        self.text_lh = {}                  # font size token → its default line height token
        self.px_of = {}                    # token name → px value (sizes)
        raw = {t['name']: t for t in d['tokens']}
        for t in d['tokens']:
            kind, v = t['type'], t['value']
            if isinstance(v, str) and v.startswith('var('):
                continue
            key = self._norm(kind, v)
            if key is not None:
                self.by.setdefault(kind, {}).setdefault(key, f"var({t['name']})")
        for name, t in raw.items():
            m = re.fullmatch(r'(--text-[\w-]+)-line-height', name)
            if m and m.group(1) in raw:
                lh = str(t['value'])
                if lh.startswith('var('):
                    lh = raw.get(lh[4:-1], {}).get('value', lh)
                self.text_lh[m.group(1)] = (f'var({name})', self._norm('lineHeight', lh))
        self.snap = {k: {self._norm(k, a) or a: b for a, b in tab.items()} for k, tab in d.get('snap', {}).items()}
        keep = d.get('keep', {})
        self.keep = {k: {self._norm(k, x) or x for x in vs} for k, vs in keep.items() if isinstance(vs, list)}
        mig = d.get('migration', {})               # tokens being retired: a layer still bound to one is rebound
        self.rebind = {k: v for k, v in mig.get('alpha_to_color_mix', {}).items()}
        self.rebind.update(mig.get('alias_then_delete', {}))
        self.weights = self.by.get('fontWeight', {})
        self.families = self.by.get('fontFamily', {})
        big = [(_px(k), v) for k, v in self.by.get('radius', {}).items() if (_px(k) or 0) >= 999]
        self.full = max(big)[1] if big else None      # the pill radius (Tailwind's rounded-full)

    @staticmethod
    def _norm(kind, v):
        v = str(v).strip()
        if kind == 'color':
            return _hex(v)
        if kind in ('fontSize', 'lineHeight', 'spacing', 'radius'):
            p = _px(v)
            return f'{p:g}px' if p is not None else v
        if kind == 'fontWeight':
            return _num(v) if _px(v) is not None else v
        if kind == 'opacity':
            return _num(float(v[:-1]) / 100) if v.endswith('%') else (_num(v) if _px(v) is not None else v)
        if kind == 'letterSpacing':
            m = re.fullmatch(r'(-?\d*\.?\d+)em', v)
            return f'{float(m.group(1)):g}em' if m else v
        if kind == 'fontFamily':
            return v.split(',')[0].strip().strip('"\'')
        return v

    def lookup(self, kind, v):
        """A literal → (css value or None, kept). kept means it stays literal on purpose."""
        n = self._norm(kind, v)
        if n is None:
            return None, False
        if n in self.keep.get(kind, ()):
            return None, True
        hit = self.by.get(kind, {}).get(n) or self.snap.get(kind, {}).get(n)
        if hit:
            return hit, False
        if kind == 'color' and len(n) == 9:
            base, a = n[:7], int(n[7:], 16)
            tok = self.by.get('color', {}).get(base)
            if tok and a == 255:
                return tok, False
            if tok:
                return f'color-mix(in oklab, {tok} {round(a / 2.55)}%, transparent)', False
        return None, False

    def bind(self, style, size=None):
        """One node's own styles → (update, left). update: {prop: css}; left: [(kind, literal)] with no token."""
        upd, left = {}, []
        fam = style.get('fontFamily')
        if fam and not str(fam).startswith(BOUND):
            first = self._norm('fontFamily', fam)
            base, _, face = first.partition('-')
            if first in self.keep.get('fontFamily', ()) or base in self.keep.get('fontFamily', ()):
                pass
            elif base in self.families:
                upd['fontFamily'] = self.families[base]
                w = FACES.get(face.lower().replace(' ', '')) if face else None
                if w and _num(w) in self.weights and not str(style.get('fontWeight', '')).startswith(BOUND):
                    upd['fontWeight'] = self.weights[_num(w)]
            else:
                left.append(('fontFamily', first))
        for prop, v in style.items():
            kind = KIND.get(prop)
            if not kind or prop == 'fontFamily' or prop in upd:
                continue
            v = str(v).strip()
            if v.startswith('var(') and v[4:-1].strip() in self.rebind:
                upd[prop] = self.rebind[v[4:-1].strip()]
                continue
            if v.startswith(BOUND) or v in ('none', 'transparent', 'currentColor', 'inherit', 'auto', 'normal') or not v:
                continue
            if kind in ('spacing', 'radius') and ' ' in v:   # shorthand: every part must have a token
                parts = [self.lookup(kind, x) for x in v.split()]
                if all(p[0] or p[1] for p in parts):
                    upd[prop] = ' '.join(p[0] or x for p, x in zip(parts, v.split()))
                elif not all(p[1] for p in parts):
                    left.append((kind, v))
                continue
            if kind == 'radius' and size and self.full:
                r, sides = _px(v), [x for x in size if x]
                if r is not None and sides and r >= 5 and r * 2 >= min(sides) - 0.5:
                    upd[prop] = self.full
                    continue
            if kind == 'margin':                              # offsets: bind an exact spacing token, else leave it
                hit = self.by.get('spacing', {}).get(self._norm('spacing', v))
                if hit:
                    upd[prop] = hit
                continue
            css, kept = self.lookup(kind, v)
            if css:
                upd[prop] = css
            elif not kept:
                left.append((kind, self._norm(kind, v) or v))
        # a line height that is its font size's default binds to that default (--text-sm-line-height)
        fs = str(upd.get('fontSize') or style.get('fontSize', ''))[4:-1]
        if 'lineHeight' in style and not str(style['lineHeight']).startswith(BOUND) and fs in self.text_lh:
            if self.text_lh[fs][1] == self._norm('lineHeight', style['lineHeight']):
                upd['lineHeight'] = self.text_lh[fs][0]
        return upd, left


# ---------- reading a frame: get_tree_summary + get_jsx, paired ----------

_LINE = re.compile(r'^( *)(\w+) "((?:[^"\\]|\\.)*)" \(([0-9A-Z]+-[0-9A-Z]+)\)(?: (\S+)×(\S+))?')


def result_text(raw):
    """A tool result as the harness saved it (JSON list of text blocks, or plain text) → the payload text."""
    try:
        d = json.loads(raw)
        if isinstance(d, list):
            raw = ''.join(x.get('text', '') for x in d if isinstance(x, dict))
    except ValueError:
        pass
    return raw


def read_tree(raw):
    """get_tree_summary text → nested {'type','name','id','w','h','kids'}."""
    raw = result_text(raw)
    m = re.search(r'"summary":\s*("(?:[^"\\]|\\.)*")', raw)
    text = json.loads(m.group(1)) if m else raw
    root, stack = None, []
    for line in text.splitlines():
        mm = _LINE.match(line)
        if not mm:
            if re.match(r'^ *\w+ "', line) or re.match(r'^ *\.\.\.', line):
                raise ValueError(f'tree cut short or unreadable: {line.strip()[:80]} (ask for a deeper depth)')
            continue                                      # the rest of a multi-line text's content
        ind, typ, name, nid, w, h = mm.groups()
        n = {'type': typ, 'name': name, 'id': nid, 'w': _px(w) if w else None, 'h': _px(h) if h else None, 'kids': []}
        depth = len(ind) // 2
        del stack[depth:]
        if stack:
            stack[-1]['kids'].append(n)
        else:
            root = n
        stack.append(n)
    return root


def read_jsx(raw):
    from .jsx import parse
    raw = result_text(raw)
    i = raw.find('}(')
    return parse(raw[i + 1:] if i >= 0 else raw[raw.find('('):])


def _els(n):
    return [c for c in n.get('children', []) if c['tag'] != '#text']


def _fits(t, j):
    tag = j['tag'].lower()
    if t['type'] == 'SVG':
        return tag == 'svg'
    if t['type'] == 'SVGVisualElement':
        return tag == t['name'].lower() or tag not in ('div', 'span', 'svg', 'img')
    if t['type'] == 'Text':
        return tag in ('div', 'span', 'p')
    return tag in ('div', 'img', 'span', 'section')


def pair(tree, jsx, out, bad):
    """Walk both in document order. out: [(node id, own styles, (w, h))]. bad: subtrees that didn't line up."""
    if not _fits(tree, jsx):
        bad.append((tree['id'], f"{tree['type']} vs <{jsx['tag']}>")); return
    style = dict(jsx.get('style', {}))
    if tree['type'] != 'Text':                        # a frame's font size is only an inherited default: Paper keeps it literal
        for k in TEXT_ONLY:
            style.pop(k, None)
    if tree['type'] in ('SVG', 'SVGVisualElement'):
        for a, prop in SVG_ATTR.items():
            if a in jsx.get('attrs', {}):
                style[prop] = jsx['attrs'][a]
    out.append((tree['id'], style, (tree['w'] or _px(style.get('width', '')), tree['h'] or _px(style.get('height', '')))))
    if tree['type'] == 'Text':
        return                                            # styled runs inside a text are not layers
    kids = _els(jsx)
    if len(kids) != len(tree['kids']):
        bad.append((tree['id'], f"{len(tree['kids'])} layers vs {len(kids)} elements")); return
    for t, j in zip(tree['kids'], kids):
        pair(t, j, out, bad)


def frame_nodes(tree_raw, jsx_raw):
    out, bad = [], []
    pair(read_tree(tree_raw), read_jsx(jsx_raw), out, bad)
    return out, bad


def plan(tokens, frames, limit=20000):
    """frames: {frame id: (tree text, jsx text)} → (payload chunks, report)."""
    groups, left, bad, counts = {}, {}, {}, {'frames': 0, 'nodes': 0, 'values': 0, 'bound_already': 0}
    for fid, (tr, jx) in frames.items():
        nodes, b = frame_nodes(tr, jx)
        if b:
            bad[fid] = b
        counts['frames'] += 1
        for nid, style, size in nodes:
            counts['bound_already'] += sum(1 for p, v in style.items() if p in KIND and str(v).startswith(BOUND))
            upd, lf = tokens.bind(style, size)
            for k in lf:
                left.setdefault(k, []).append(nid)
            if upd:
                counts['nodes'] += 1; counts['values'] += len(upd)
                groups.setdefault(json.dumps(upd, sort_keys=True), []).append(nid)
    entries = sorted(({'nodeIds': ids, 'styles': json.loads(k)} for k, ids in groups.items()), key=lambda e: -len(e['nodeIds']))
    chunks, cur, size = [], [], 2
    for e in entries:
        ids = e['nodeIds']
        while ids:                                        # split a group whose ids alone pass the limit
            room = max(1, (limit - size - len(json.dumps(e['styles'])) - 30) // 10)
            part, ids = ids[:room], ids[room:]
            ent = {'nodeIds': part, 'styles': e['styles']}
            n = len(json.dumps(ent)) + 2
            if cur and size + n > limit:
                chunks.append(cur); cur, size = [], 2
            cur.append(ent); size += n
    if cur:
        chunks.append(cur)
    return chunks, {'counts': counts, 'left': left, 'bad': bad}


# ---------- generated HTML (explorations, promoted screens): literals → tokens before it is pasted ----------

def _camel(k):
    return re.sub(r'-([a-z])', lambda m: m.group(1).upper(), k.strip())


def _kebab(k):
    return re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), k)


def _decls(css):
    """'a:b;c:url(x;y)' → [(prop, value)], splitting only on semicolons outside brackets."""
    out, depth, cur = [], 0, ''
    for ch in css:
        depth += ch == '('
        depth -= ch == ')'
        if ch == ';' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [(d.split(':', 1)[0].strip(), d.split(':', 1)[1].strip()) for d in out if ':' in d]


def tokenize(html, tokens, left=None):
    """Every inline style and SVG fill/stroke in html, bound to tokens where one fits. Values with no token are kept
    and, if `left` (a dict) is given, counted there, so a spec can show what still needs a token."""
    def color(v):
        css, kept = tokens.lookup('color', v)
        if not css and not kept and left is not None:
            left[('color', _hex(v) or v)] = left.get(('color', _hex(v) or v), 0) + 1
        return css or v

    def style(m):
        decls = _decls(m.group(2))
        st = {}
        for k, v in decls:
            ck = _camel(k)
            if ck == 'background' and _hex(v):
                ck = 'backgroundColor'
            st[ck] = v
        w, h = _px(st.get('width', '')), _px(st.get('height', ''))
        upd, lf = tokens.bind({k: v for k, v in st.items() if k in KIND}, (w, h))
        if left is not None:
            for x in lf:
                left[x] = left.get(x, 0) + 1
        parts = []
        for k, v in decls:
            ck = _camel(k)
            if ck == 'background' and _hex(v):
                ck = 'backgroundColor'
            if ck in upd:
                parts.append(f'{_kebab(ck)}:{upd.pop(ck)}')
            elif ck in ('border', 'borderTop', 'borderBottom', 'borderLeft', 'borderRight', 'outline'):
                parts.append(f'{k}:' + re.sub(r'#[0-9A-Fa-f]{3,8}\b', lambda c: color(c.group(0)), v))
            else:
                parts.append(f'{k}:{v}')
        parts += [f'{_kebab(k)}:{v}' for k, v in upd.items()]      # a face name added its weight
        return f'{m.group(1)}"{";".join(parts)}"'

    def attr(m):
        return f'{m.group(1)}={m.group(2)}{color(m.group(3))}{m.group(2)}'

    html = re.sub(r'(style=)"([^"]*)"', style, html)
    return re.sub(r'\b(fill|stroke|stop-color)=(["\'])(#[0-9A-Fa-f]{3,8}|rgba?\([^)]*\))\2', attr, html)
