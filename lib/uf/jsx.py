"""Real frames across Paper files: get_jsx (inline-styles) output → pasteable HTML.

Live copies (<x-paper-clone>) only work inside one file. When a project keeps its library in one Paper file and
its maps in another, a screen is copied as its real layers instead: fetch the frame's JSX once
(get_jsx(format "inline-styles")), keep it in design/user-flow/frames/<node id>.jsx, and the renderer inlines the
converted HTML. The copy is real layers at real size, never an image; it's a snapshot, refreshed with `stale`.

    tree = parse(jsx_text)            # nested dicts: {'tag', 'attrs', 'style', 'children', 'text'}
    html = to_html(tree, size=(390, 844), layer='DO6 · Links tab')
    composite(top_tree, fill_tree)    # a top-only frame (empty sheet) with the sheet of another frame
"""
import re

_DROP = {'boxSizing', 'fontSynthesis', 'MozOsxFontSmoothing', 'WebkitFontSmoothing', 'overflowWrap', 'x', 'y'}
_UNITLESS = {'fontWeight', 'opacity', 'flex', 'flexGrow', 'flexShrink', 'zIndex', 'order', 'lineHeight'}
_SVG_KEEP = {'viewBox', 'preserveAspectRatio', 'gradientTransform', 'gradientUnits', 'patternUnits',
             'patternTransform', 'clipPathUnits', 'maskUnits', 'markerWidth', 'markerHeight', 'refX', 'refY'}
_VOID = {'img', 'br', 'hr', 'input', 'meta', 'link'}


def _kebab(k):
    if k.startswith('Moz'):
        k = '-moz-' + k[3:]
    elif k.startswith('Webkit'):
        k = '-webkit-' + k[6:]
    elif k.startswith('ms'):
        k = '-ms-' + k[2:]
    return re.sub(r'([A-Z])', lambda m: '-' + m.group(1).lower(), k)


def _style_obj(src):
    """'{ alignItems: 'center', gap: 16, fontFamily: '"A", "B"' }' → {key: value}"""
    out = {}
    for m in re.finditer(r"(\w+)\s*:\s*('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|[-\w.%]+)", src):
        k, v = m.group(1), m.group(2)
        if v[0] in '\'"':
            v = v[1:-1]
        out[k] = v
    return out


def _css(style):
    parts = []
    for k, v in style.items():
        if k in _DROP:
            continue
        v = str(v).replace('"', "'")
        if re.fullmatch(r'-?[\d.]+', v) and k not in _UNITLESS:
            v += 'px'
        if v == 'calc(infinity * 1px)':
            v = '9999px'
        if k == 'overflow' and v == 'clip':
            v = 'hidden'
        parts.append(f'{_kebab(k)}:{v}')
    return ';'.join(parts)


_TOKEN = re.compile(r'<(/?)([\w.:-]+)((?:[^<>{}"\']|"[^"]*"|\'[^\']*\'|\{\{.*?\}\}|\{[^{}]*\})*?)(/?)>|([^<]+)', re.S)
_ATTR = re.compile(r'([\w:-]+)(?:=("[^"]*"|\'[^\']*\'|\{\{.*?\}\}|\{[^{}]*\}))?', re.S)


def parse(jsx):
    text = jsx.strip()
    text = re.sub(r'^\(\s*', '', text)
    text = re.sub(r'\s*\)\s*$', '', text)
    root = {'tag': '#root', 'children': []}
    stack = [root]
    for m in _TOKEN.finditer(text):
        closing, tag, attrs, selfclose, txt = m.groups()
        if txt is not None:
            t = txt.strip()
            if t:
                t = re.sub(r"\{\s*'((?:[^'\\]|\\.)*)'\s*\}|\{\s*\"((?:[^\"\\]|\\.)*)\"\s*\}", lambda x: x.group(1) or x.group(2) or '', t)
                t = re.sub(r'\s+', ' ', t)
                stack[-1]['children'].append({'tag': '#text', 'text': t})
            continue
        if closing:
            while len(stack) > 1:
                n = stack.pop()
                if n['tag'] == tag:
                    break
            continue
        node = {'tag': tag, 'attrs': {}, 'style': {}, 'children': []}
        for a in _ATTR.finditer(attrs or ''):
            k, v = a.group(1), a.group(2)
            if v is None:
                continue
            if k == 'style' and v.startswith('{{'):
                node['style'] = _style_obj(v[2:-2])
            elif v.startswith('{'):
                node['attrs'][k] = v[1:-1].strip().strip('\'"')
            else:
                node['attrs'][k] = v[1:-1]
        stack[-1]['children'].append(node)
        if not selfclose and tag not in _VOID:
            stack.append(node)
    kids = [c for c in root['children'] if c['tag'] != '#text']
    return kids[0] if kids else None


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _attr_name(k, in_svg):
    if k == 'className':
        return 'class'
    if in_svg and k not in _SVG_KEEP:
        return _kebab(k)
    return k


def to_html(node, size=None, layer=None, _svg=False):
    if node['tag'] == '#text':
        return _esc(node['text'])
    tag = node['tag']
    svg = _svg or tag == 'svg'
    style = dict(node.get('style', {}))
    if size:
        style.setdefault('width', f'{size[0]}px')
        if size[1]:
            style.setdefault('height', f'{size[1]}px')
        style.pop('position', None)
        style['position'] = 'relative'
    attrs = ''.join(f' {_attr_name(k, svg)}="{v}"' for k, v in node.get('attrs', {}).items() if k not in ('key',))
    if layer:
        attrs = f' layer-name="{_esc(layer)}"' + attrs
    css = _css(style)
    open_ = f'<{tag}{attrs}' + (f' style="{css}"' if css else '') + '>'
    if tag in _VOID:
        return open_
    inner = ''.join(to_html(c, _svg=svg) for c in node.get('children', []))
    return f'{open_}{inner}</{tag}>'


# ---------------- composites: a top-only frame with a real sheet
def _is_sheet(n):
    s = n.get('style', {})
    return (n.get('tag') == 'div' and str(s.get('backgroundColor', '')).upper() in ('#FFFFFF', '#FFF', 'WHITE')
            and ('borderTopLeftRadius' in s or 'borderRadius' in s) and str(s.get('width', '')).startswith('390'))


def sheet_of(frame):
    """The frame's sheet (the white panel under the bar), or None."""
    for c in frame.get('children', []):
        if c.get('tag') != '#text' and _is_sheet(c):
            return c
    return None


def is_empty_sheet(frame):
    s = sheet_of(frame)
    return s is not None and not [c for c in s.get('children', []) if c.get('tag') != '#text']


def composite(top, fill):
    """`top` with its (empty) sheet replaced by `fill`'s sheet, cut to the empty sheet's height."""
    import copy
    top = copy.deepcopy(top)
    target = sheet_of(top)
    src = sheet_of(fill)
    if target is None or src is None:
        return top
    new = copy.deepcopy(src)
    new['style']['height'] = target['style'].get('height', new['style'].get('height'))
    new['style']['overflow'] = 'clip'
    new['style'].pop('minHeight', None)
    kids = top['children']
    kids[kids.index(target)] = new
    return top
