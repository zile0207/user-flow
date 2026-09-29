"""Shared pieces for every user-flow board: palette, text, icons, chunk output."""
import os

# Board palette. Neutral on purpose: the boards describe the app, they are not the app.
INK = "#171B1D"; MUTED = "#4B585B"; LINE = "#E3E7E8"; GREY = "#8E999C"; AMBER = "#B7791F"
ACCENT = "#E05254"      # the persona's path and chosen designs. init sets it from the project's brand colour.
F = "font-family:'Switzer', system-ui, sans-serif;"
PW, PH = 390, 844       # device frame for exploration screens (iPhone)


def set_theme(accent=None, font=None, device=None):
    global ACCENT, F, PW, PH
    if accent: ACCENT = accent
    if font: F = f"font-family:'{font}', system-ui, sans-serif;"
    if device: PW, PH = device


def nid(node):
    """A Paper node id: '1QM5' → '1QM5-0'."""
    node = str(node)
    return node if '-' in node else node + '-0'


# Cross-file mode (set by project.Project): the library lives in another Paper file, so screens are inlined as
# converted real layers from design/user-flow/frames/<node>.jsx instead of live copies.
CROSS_FILE = False
FRAMES_DIR = None
FRAME_NAMES = {}          # node → frame name (from library.json), for the copy's layer name
MISSING = set()           # frames a render needed but the cache doesn't have yet
LOCAL_MODE = False        # the maps file has a Frames page: one real copy of each screen, typed once
LOCAL = {}                # key ('<node>' or '<node>+<sheet node>') → the copy's node id on the Frames page
LOCAL_NEEDED = {}         # key → (node, sheet) a render needed that isn't on the Frames page yet
USED = set()              # every library frame a render showed (bind-tokens binds a board's frames from this)


def frame_key(node, sheet=None):
    return nid(node) + (f'+{nid(sheet)}' if sheet else '')
NOSCALE = ('<!--uf:noscale-->', '<!--/uf:noscale-->')


def _frame_html(node, sheet=None, name=None):
    import os
    from . import jsx
    def load(n):
        p = os.path.join(FRAMES_DIR or '', f'{nid(n)}.jsx')
        if not os.path.exists(p):
            MISSING.add(nid(n)); return None
        raw = open(p).read()
        return jsx.parse(raw[raw.find('('):] if '(' in raw else raw)
    top = load(node)
    fill = load(sheet) if sheet else None
    if top is None or (sheet and fill is None):
        return None
    tree = jsx.composite(top, fill) if fill is not None else top
    name = name or FRAME_NAMES.get(nid(node), nid(node)) + (f' + sheet of {FRAME_NAMES.get(nid(sheet), nid(sheet))}' if sheet else '')
    return jsx.to_html(tree, size=(PW, None), layer=name)


def screen(node, w, radius=10, layer='Screen', sheet=None, name=None):
    """A real screen on a board: a live copy of the Paper frame `node`, in a box w wide (in the board's spec units).
    Never an image. Boards are scaled (Board(scale=…)) so this box comes out at the device width: the zoom then
    cancels out and is dropped, and the frame sits at its real size, 1:1. The box clips frames taller than the device."""
    assert node, 'a screen needs the Paper node id of a real frame (boards never show images)'
    USED.update(nid(n) for n in (node, sheet) if n)
    z = w / PW
    h = w * PH / PW
    box = (f'<div layer-name="{layer}" style="position:relative;width:{w}px;height:{h:.4f}px;flex-shrink:0;overflow:hidden;'
           f'border-radius:{radius}px;background:#FFFFFF">')
    if not CROSS_FILE and not sheet:
        return box + f'<x-paper-clone node-id="{nid(node)}" style="position:absolute;left:0px;top:0px;zoom:{z:.6f}" /></div>'
    if LOCAL_MODE:              # a live copy of this screen's copy on the Frames page (same file: cheap)
        key = frame_key(node, sheet)
        if key in LOCAL:
            return box + f'<x-paper-clone node-id="{LOCAL[key]}" style="position:absolute;left:0px;top:0px;zoom:{z:.6f}" /></div>'
        LOCAL_NEEDED[key] = (nid(node), nid(sheet) if sheet else None)
        return box + f'<div style="padding:8px;font-size:10px;line-height:13px;color:#B7791F">{key} not on the Frames page yet</div></div>'
    html = _frame_html(node, sheet, name)       # name: the copy's layer name (a board names it by its own step)
    if html is None:            # not fetched yet: a visible marker, and the render reports what to fetch
        return box + f'<div style="padding:8px;font-size:10px;line-height:13px;color:#B7791F">frame {nid(node)} not fetched</div></div>'
    # the frame keeps its real size: the board's scale must not touch it, and the box comes out at the device width
    return box + NOSCALE[0] + f'<div style="position:absolute;left:0px;top:0px;width:{PW}px;height:{PH}px;overflow:hidden">' + html + '</div>' + NOSCALE[1] + '</div>'


def t(txt, size, lh, w, col, extra=''):
    return f'<div style="{F}font-size:{size}px;line-height:{lh}px;font-weight:{w};color:{col};{extra}">{txt}</div>'


ICON = {
    'check': 'M20 6 9 17l-5-5',
    'arrow': 'M5 12h14M13 6l6 6-6 6',
}


def ico(name_or_path, size=22, col='#FFFFFF', sw=2):
    p = ICON.get(name_or_path, name_or_path)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{p}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def dump(chunks, folder):
    """Write chunks as NN.html. Paste each one with write_html (insert-children), byte for byte."""
    os.makedirs(folder, exist_ok=True)
    for f in os.listdir(folder):
        if f.endswith('.html'):
            os.remove(os.path.join(folder, f))
    for i, c in enumerate(chunks):
        open(os.path.join(folder, f'{i:02d}.html'), 'w').write(c)
    print(len(chunks), 'chunks,', sum(len(c) for c in chunks), 'chars →', folder)
