"""Master map: every screen in the app, grouped by area, with every gap in place. An inventory, not a flow.
Arrows live in journey and flow maps; the master map answers "what exists, and what is missing".
Rules: references/nodes-and-layout.md · Master map."""
import math
from . import base
from .base import t, dump, INK, MUTED, LINE, AMBER

CARD_W, CARD_H, THUMB_W, THUMB_H = 140, 352, 124, 268
GAP = 16
COLS = 6                                   # cards per row inside an area
AREA_W = COLS * CARD_W + (COLS - 1) * GAP + 48
COL_GAP = 48
TOP = 300


class MasterMap:
    def __init__(self, project, columns=5):
        self.P = project
        self.columns = columns
        self.areas = []

    def area(self, name, sub, items, entries=''):
        """items: ('card', img, ref, title) for a designed screen · ('gap', gid) for a registry gap."""
        self.areas.append(dict(name=name, sub=sub, items=items, entries=entries))

    # ---------------- pieces
    def _card(self, img, ref, title):
        return (f'<div layer-name="{ref} · {title}" style="width:{CARD_W}px;height:{CARD_H}px;background:#FFFFFF;border:1px solid {LINE};border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;box-sizing:border-box">'
                f'<img src="paper-asset://{self.P.img_dir}/{img}.png" style="width:{THUMB_W}px;height:{THUMB_H}px;border-radius:8px;border:1px solid {LINE};object-fit:cover;flex-shrink:0" />'
                + t(ref, 10, 13, 700, MUTED, 'letter-spacing:0.06em;padding:0 2px;') + t(title, 12, 15, 700, INK, 'padding:0 2px;') + '</div>')

    def _gap(self, gid):
        g = self.P.gap(gid); st = g.get('state', 'todo')
        if st == 'explored':
            return (f'<div layer-name="{gid} · {g["title"]} · explored" style="width:{CARD_W}px;height:{CARD_H}px;background:#FFFFFF;border:1px solid {LINE};border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;box-sizing:border-box">'
                    f'<img src="paper-asset://{self.P.img_dir}/{g["img"]}.png" style="width:{THUMB_W}px;height:{THUMB_H}px;border-radius:8px;border:1px solid {LINE};object-fit:cover;flex-shrink:0" />'
                    + t(f'{gid} · EXPLORED', 10, 13, 700, base.ACCENT, 'letter-spacing:0.06em;padding:0 2px;') + t(g['title'], 12, 15, 700, INK, 'padding:0 2px;') + '</div>')
        col, bd = (('#6B7678', '#D3D8DA') if st == 'later' else (AMBER, '#B4BDBF'))
        tag = {'later': 'AFTER MVP', 'exploring': 'EXPLORING'}.get(st, 'NEEDS DESIGN')
        return (f'<div layer-name="To design · {g["title"]}" style="width:{CARD_W}px;height:{CARD_H}px;background:#FBFBFA;border:1.5px dashed {bd};border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;box-sizing:border-box">'
                f'<div style="width:{THUMB_W}px;height:{THUMB_H}px;flex-shrink:0;border-radius:8px;background:#F1F3F3;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px;padding:10px;box-sizing:border-box">'
                + t(tag, 9, 11, 700, col, 'letter-spacing:0.08em;text-align:center;') + t(g['need'], 11, 15, 500, MUTED, 'text-align:center;') + '</div>'
                + t(gid, 10, 13, 700, col, 'letter-spacing:0.06em;padding:0 2px;') + t(g['title'], 12, 15, 700, INK, 'padding:0 2px;') + '</div>')

    def _area_h(self, a):
        rows = max(1, math.ceil(len(a['items']) / COLS))
        return 24 + 62 + (22 if a['entries'] else 0) + rows * CARD_H + (rows - 1) * GAP + 24

    def _area_html(self, a, x, y):
        cells = ''.join(self._card(*it[1:]) if it[0] == 'card' else self._gap(it[1]) for it in a['items'])
        n_card = sum(1 for it in a['items'] if it[0] == 'card')
        n_gap = sum(1 for it in a['items'] if it[0] == 'gap' and self.P.gap(it[1]).get('state') in ('todo', 'exploring'))
        count = f'{n_card} designed' + (f' · {n_gap} to design' if n_gap else '')
        return (f'<div layer-name="Area · {a["name"]}" style="position:absolute;left:{x}px;top:{y}px;width:{AREA_W}px;height:{self._area_h(a)}px;background:#F6F7F7;border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
                f'<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px">'
                + '<div style="display:flex;flex-direction:column;gap:2px">' + t(a['name'], 22, 27, 700, INK, 'letter-spacing:-0.015em;') + t(a['sub'], 12, 16, 500, MUTED) + '</div>'
                + t(count, 12, 16, 700, AMBER if n_gap else MUTED, 'white-space:nowrap;') + '</div>'
                + (t('Entry points: ' + a['entries'], 12, 16, 500, MUTED) if a['entries'] else '')
                + f'<div style="display:flex;flex-wrap:wrap;gap:{GAP}px">{cells}</div></div>')

    def render(self, title, right, story):
        W = 40 * 2 + self.columns * AREA_W + (self.columns - 1) * COL_GAP
        heights = [TOP] * self.columns
        placed = []
        for a in self.areas:                       # masonry: each area goes into the shortest column
            c = heights.index(min(heights))
            placed.append((a, 40 + c * (AREA_W + COL_GAP), heights[c]))
            heights[c] += self._area_h(a) + COL_GAP
        H = max(heights) + 40
        designed = sum(1 for a in self.areas for it in a['items'] if it[0] == 'card')
        gids = [it[1] for a in self.areas for it in a['items'] if it[0] == 'gap']
        states = [self.P.gap(g).get('state', 'todo') for g in gids]
        designed += states.count('explored')
        todo = states.count('todo') + states.count('exploring')
        later = states.count('later')
        bar = (f'<div layer-name="Header bar" style="position:absolute;left:40px;top:40px;width:{W-80}px;height:56px;background:{INK};border-radius:14px;display:flex;align-items:center;padding:0 20px;gap:16px;box-sizing:border-box">'
               + t('Master map', 13, 18, 500, '#9AA4A6') + '<div style="width:1px;height:20px;background:#3A4245"></div>' + t(title, 17, 22, 700, '#FFFFFF')
               + '<div style="flex:1"></div>' + t(right, 13, 18, 500, '#9AA4A6') + f'<div style="width:10px;height:10px;border-radius:5px;background:{base.ACCENT}"></div></div>')
        stats = [(str(designed), 'designed screens', INK), (str(todo), 'to design', AMBER)] + ([(str(later), 'after MVP', '#6B7678')] if later else []) + [(str(len(self.areas)), 'areas', INK)]
        top = (bar + f'<div layer-name="Story line" style="position:absolute;left:40px;top:116px;width:2600px">' + t(story, 17, 24, 500, MUTED) + '</div>'
               + f'<div layer-name="Coverage" style="position:absolute;left:{W-700}px;top:160px;width:660px;display:flex;justify-content:flex-end;gap:36px">'
               + ''.join('<div style="display:flex;flex-direction:column;gap:2px;align-items:flex-end">' + t(n, 32, 36, 700, c, 'letter-spacing:-0.02em;') + t(l, 12, 16, 500, MUTED, 'white-space:nowrap;') + '</div>' for n, l, c in stats) + '</div>')
        chunks = [top] + [self._area_html(a, x, y) for a, x, y in placed]
        dump(chunks, self.P.out('master'))
        print(f'artboard {W} x {H} · {designed} designed · {todo} to design · {later} after MVP · {len(self.areas)} areas')
        return W, H
