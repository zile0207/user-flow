"""Exploration board template. Give it a spec (see TEMPLATE.md); it returns Paper HTML chunks.

The layout is fixed, so every board looks the same:
  header bar · left column (the gap, must do, where it sits, references) · rounds on the right,
  each round = a round label, directions side by side (head, screens, labels, notes), then a pick bar
  or, once confirmed, a confirmed bar.
"""
import math
from . import base
from .base import t, dump, ico, INK, MUTED, LINE, AMBER, GREY

PAD = 40
LEFT_W = 840
X0 = PAD + LEFT_W + 120          # rounds start here
DIR_GAP = 80
SCREEN_GAP = 40
REF_W = 256                      # 3 references per row
REF_H = 581                      # Mobbin screenshots are 1179 x 2676
BRIEF_TOP = 136
REFS_TOP = 800
ROUND_LABEL_H = 64
HEAD_H = 96
LABEL_H = 34
NOTES_H = 120
BAR_H = 92
ROUND_GAP = 120


def dir_width(d):
    n = len(d['screens'])
    return n * base.PW + (n - 1) * SCREEN_GAP


def round_width(r):
    return sum(dir_width(d) for d in r['directions']) + DIR_GAP * (len(r['directions']) - 1)


def round_height(r, last):
    return ROUND_LABEL_H + HEAD_H + base.PH + 16 + LABEL_H + NOTES_H + (24 + BAR_H if last else 0)


def refs_height(n):
    rows = max(1, math.ceil(n / 3))
    return 34 + rows * (REF_H + 58) + (rows - 1) * 28


def size(spec):
    w = max(X0 + max(round_width(r) for r in spec['rounds']) + PAD, 3000)
    rounds_h = BRIEF_TOP + sum(round_height(r, i == len(spec['rounds']) - 1) for i, r in enumerate(spec['rounds'])) + ROUND_GAP * (len(spec['rounds']) - 1)
    left_h = REFS_TOP + refs_height(len(spec['refs']))
    return w, max(rounds_h, left_h) + PAD + 20


def label(s, col=INK):
    return t(s, 12, 16, 700, col, 'letter-spacing:0.08em;white-space:nowrap;')


# ---------------- chrome
def header(spec, W):
    st = spec['status']
    if st['state'] == 'confirmed':
        right = f"Confirmed · {st['chosen']} · round {st['round']} · {st['date']}"; dot = base.ACCENT
    else:
        right = f"Exploring · round {len(spec['rounds'])} · {spec['source']} · {st['date']}"; dot = AMBER
    return (f'<div layer-name="Header bar" style="position:absolute;left:{PAD}px;top:40px;width:{W-2*PAD}px;height:56px;background:{INK};border-radius:14px;display:flex;align-items:center;padding:0 20px;gap:16px;box-sizing:border-box">'
            + t('Explore', 13, 18, 500, '#9AA4A6') + '<div style="width:1px;height:20px;background:#3A4245"></div>'
            + t(f"{spec['id']} · {spec['title']}", 17, 22, 700, '#FFFFFF') + '<div style="flex:1"></div>'
            + t(right, 13, 18, 500, '#9AA4A6') + f'<div style="width:10px;height:10px;border-radius:5px;background:{dot}"></div></div>')


def where_box(kind, top, main, sub=''):
    if kind == 'this':
        return (f'<div style="width:160px;height:76px;border:1.5px dashed #B4BDBF;border-radius:6px;background:#FBFBFA;display:flex;flex-direction:column;justify-content:center;padding:0 12px;box-sizing:border-box;gap:2px">'
                + t(top, 10, 12, 700, AMBER, 'letter-spacing:0.08em;') + t(main, 13, 17, 700, INK) + '</div>')
    if kind == 'outside':
        return (f'<div style="width:160px;height:76px;border:1.5px dashed {INK};border-radius:6px;display:flex;flex-direction:column;justify-content:center;padding:0 12px;box-sizing:border-box;gap:2px">'
                + t(top, 10, 12, 700, MUTED, 'letter-spacing:0.08em;') + t(main, 13, 17, 700, INK) + '</div>')
    # kind == 'screen': top = image path
    return (f'<div style="display:flex;align-items:center;gap:10px"><img src="paper-asset://{top}" style="width:60px;height:130px;border-radius:6px;border:1px solid {LINE};object-fit:cover" />'
            + '<div style="display:flex;flex-direction:column;gap:2px;width:110px">' + t(main, 13, 17, 700, INK) + t(sub, 12, 16, 500, MUTED) + '</div></div>')


def brief(spec):
    b = spec['brief']
    musts = ''.join('<div style="display:flex;gap:10px;align-items:flex-start">' + ico('check', 16, base.ACCENT, 2.6) + t(m, 14, 20, 500, INK) + '</div>' for m in b['musts'])
    arrow = ico('arrow', 22, GREY, 2)
    chain = arrow.join(where_box(*w) for w in b['where'])
    return (f'<div layer-name="Brief" style="position:absolute;left:{PAD}px;top:{BRIEF_TOP}px;width:{LEFT_W}px;display:flex;flex-direction:column;gap:22px">'
            + label('THE GAP', AMBER) + t(spec['title'], 40, 44, 700, INK, 'letter-spacing:-0.025em;') + t(b['needs'], 17, 25, 500, MUTED)
            + '<div style="display:flex;flex-direction:column;gap:10px">' + label('MUST DO') + musts + '</div>'
            + '<div style="display:flex;flex-direction:column;gap:12px">' + label('WHERE IT SITS') + f'<div style="display:flex;align-items:center;gap:12px">{chain}</div></div>'
            + '</div>')


def refs(spec):
    src = 'From you' if spec['refs_source'] == 'user' else 'None given, so these come from Mobbin'
    cells = ''.join(f'<div style="display:flex;flex-direction:column;gap:6px;width:{REF_W}px"><img src="paper-asset://{r["img"]}" style="width:{REF_W}px;height:{REF_H}px;border-radius:12px;border:1px solid {LINE};object-fit:cover;object-position:top" />'
                    + t(r['name'], 15, 20, 700, INK) + t(r['take'], 13, 18, 500, MUTED) + '</div>' for r in spec['refs'])
    return (f'<div layer-name="References" style="position:absolute;left:{PAD}px;top:{REFS_TOP}px;width:{LEFT_W}px;display:flex;flex-direction:column;gap:16px">'
            + '<div style="display:flex;align-items:baseline;gap:10px">' + label('REFERENCES') + t(src, 13, 16, 500, MUTED) + '</div>'
            + f'<div style="display:flex;flex-wrap:wrap;column-gap:36px;row-gap:28px">{cells}</div></div>')


# ---------------- rounds
def round_blocks(spec, W):
    out = []
    y = BRIEF_TOP
    st = spec['status']
    for ri, r in enumerate(spec['rounds']):
        last = ri == len(spec['rounds']) - 1
        n = ri + 1
        ask = r.get('ask')
        out.append(f'<div layer-name="Round {n}" style="position:absolute;left:{X0}px;top:{y}px;width:{W-X0-PAD}px;display:flex;align-items:baseline;gap:14px;padding-bottom:12px;border-bottom:1px solid {LINE}">'
                   + label(f'ROUND {n}', AMBER) + t(f"{len(r['directions'])} directions · {r['date']}", 13, 18, 500, MUTED)
                   + (t(f'You asked: {ask}', 15, 20, 600, INK) if ask else '') + '</div>')
        dy = y + ROUND_LABEL_H
        x = X0
        for d in r['directions']:
            w = dir_width(d)
            chosen = st['state'] == 'confirmed' and st['chosen'] == d['letter']
            if chosen:
                out.append(f'<div layer-name="Chosen outline" style="position:absolute;left:{x-20}px;top:{dy-18}px;width:{w+40}px;height:{HEAD_H+base.PH+16+LABEL_H+NOTES_H+30}px;border:3px solid {base.ACCENT};border-radius:28px;box-sizing:border-box"></div>')
            badge_bg = base.ACCENT if chosen else INK
            parent = f' · from {d["from"]}' if d.get('from') else ''
            out.append(f'<div layer-name="Direction {d["letter"]}" style="position:absolute;left:{x}px;top:{dy}px;width:{w}px;display:flex;flex-direction:column;gap:8px">'
                       + '<div style="display:flex;align-items:center;gap:12px">'
                       + f'<div style="width:36px;height:36px;border-radius:18px;background:{badge_bg};display:flex;align-items:center;justify-content:center;flex-shrink:0">' + t(d['letter'], 17, 22, 700, '#FFFFFF') + '</div>'
                       + t(d['title'], 26, 31, 700, INK, 'letter-spacing:-0.02em;white-space:nowrap;')
                       + (t(parent, 15, 20, 600, MUTED, 'white-space:nowrap;') if parent else '')
                       + (f'<div style="background:{base.ACCENT};border-radius:999px;padding:5px 12px">' + t('CHOSEN', 11, 14, 700, '#FFFFFF', 'letter-spacing:0.08em;') + '</div>' if chosen else '')
                       + '</div>' + t(d['idea'], 15, 21, 500, MUTED) + '</div>')
            sy = dy + HEAD_H
            out.append(f'<div layer-name="Direction {d["letter"]} · screens" style="position:absolute;left:{x}px;top:{sy}px;width:{w}px;display:flex;gap:{SCREEN_GAP}px">'
                       + ''.join(s['html'] for s in d['screens']) + '</div>')
            ly = sy + base.PH + 16
            out.append(f'<div layer-name="Direction {d["letter"]} · labels" style="position:absolute;left:{x}px;top:{ly}px;width:{w}px;display:flex;gap:{SCREEN_GAP}px">'
                       + ''.join(f'<div style="width:{base.PW}px">' + t(f'{d["letter"]}·{i+1} · {s["label"]}', 14, 18, 700, INK) + '</div>' for i, s in enumerate(d['screens'])) + '</div>')
            out.append(f'<div layer-name="Direction {d["letter"]} · notes" style="position:absolute;left:{x}px;top:{ly+LABEL_H}px;width:{w}px;display:flex;flex-direction:column;gap:6px;padding-top:12px;border-top:1px solid {LINE}">'
                       + t('Good: ' + d['good'], 14, 20, 500, INK) + t('Costs: ' + d['costs'], 14, 20, 500, MUTED) + t('Inspired by ' + d['inspired'], 13, 18, 500, GREY) + '</div>')
            x += w + DIR_GAP
        y = dy + HEAD_H + base.PH + 16 + LABEL_H + NOTES_H
        if last:
            by = y + 24
            if st['state'] == 'confirmed':
                txt = f"{st['chosen']} is confirmed. It replaced {spec['id']} on {spec['journey']['name']}, {st['date']}. Earlier rounds stay here for the record."
                out.append(f'<div layer-name="Confirmed" style="position:absolute;left:{X0}px;top:{by}px;width:{W-X0-PAD}px;height:{BAR_H}px;background:#FDF1F1;border:2px solid {base.ACCENT};border-radius:20px;padding:0 32px;display:flex;align-items:center;gap:24px;box-sizing:border-box">'
                           + label('CONFIRMED', base.ACCENT) + t(txt, 16, 22, 500, INK) + '</div>')
            else:
                letters = ', '.join(d['letter'] for d in r['directions'])
                txt = f'Reply with one of: confirm {letters.split(", ")[0]} · iterate on {letters.split(", ")[0]} ("smaller, keep the live places") · more variants · mix ("A\'s size with B\'s places"). The next round goes below this one.'
                out.append(f'<div layer-name="Your pick" style="position:absolute;left:{X0}px;top:{by}px;width:{W-X0-PAD}px;height:{BAR_H}px;background:#F6F7F7;border-radius:20px;padding:0 32px;display:flex;align-items:center;gap:24px;box-sizing:border-box">'
                           + label('YOUR PICK', AMBER) + t(txt, 16, 22, 500, INK) + '</div>')
        y += ROUND_GAP
    return out


def render(spec, folder):
    W, H = size(spec)
    chunks = [header(spec, W) + brief(spec), refs(spec)] + round_blocks(spec, W)
    dump(chunks, folder)
    print('artboard', W, 'x', H)
    return W, H


# ---------------- journey card after confirm
def explored_card(spec, x, y, img_path):
    """Replaces the dashed card on the journey map. Same size and position, so arrows still line up."""
    st = spec['status']
    return (f'<div layer-name="{spec["id"]} · {spec["title"]} · explored" style="position:absolute;left:{x}px;top:{y}px;width:200px;height:520px;background:#FFFFFF;border:1px solid {LINE};border-radius:16px;padding:10px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
            f'<div style="position:relative;width:180px;height:390px;flex-shrink:0">'
            f'<img src="paper-asset://{img_path}" style="width:180px;height:390px;border-radius:10px;border:1px solid {LINE};object-fit:cover" />'
            f'<div style="position:absolute;left:8px;top:8px;background:{base.ACCENT};border-radius:999px;padding:4px 9px">' + t(f'EXPLORED · {st["chosen"]}', 10, 12, 700, '#FFFFFF', 'letter-spacing:0.08em;') + '</div></div>'
            '<div style="display:flex;flex-direction:column;gap:3px;padding:0 4px">'
            + t(spec['id'], 11, 14, 700, base.ACCENT, 'letter-spacing:0.06em;') + t(spec['title'], 15, 19, 700, INK)
            + t(f'Chosen: {st["chosen"]}, round {st["round"]}. See Explore · {spec["id"]}.', 12, 16, 500, MUTED) + '</div></div>')
