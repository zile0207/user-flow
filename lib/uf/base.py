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


def screen(node, w, radius=10, layer='Screen'):
    """A real screen on a board: a live copy of the Paper frame `node`, in a box w wide (in the board's spec units).
    Never an image. Boards are scaled (Board(scale=…)) so this box comes out at the device width: the zoom then
    cancels out and is dropped, and the frame sits at its real size, 1:1. The box clips frames taller than the device."""
    assert node, 'a screen needs the Paper node id of a real frame (boards never show images)'
    z = w / PW
    h = w * PH / PW
    return (f'<div layer-name="{layer}" style="position:relative;width:{w}px;height:{h:.4f}px;flex-shrink:0;overflow:hidden;'
            f'border-radius:{radius}px;background:#FFFFFF">'
            f'<x-paper-clone node-id="{nid(node)}" style="position:absolute;left:0px;top:0px;zoom:{z:.6f}" /></div>')


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
