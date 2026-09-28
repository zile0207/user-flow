"""State map: every state one piece of UI can show, in priority order, with when each shows, when it ends,
and what it gives way to. For a surface that shows one thing at a time (a top card, a banner, a now-playing bar).
Rules: references/nodes-and-layout.md · State maps."""
from . import base, board
from .base import t, INK, MUTED, LINE, AMBER

CARD_W, CARD_H, THUMB_W, THUMB_H = 140, 352, 124, 268
ROW_GAP = 28
LEFT = 40
PRI_W = 64
NAME_W = 260
VAR_GAP = 16
TEXT_W = 900


class StateMap:
    def __init__(self, project, element, rule):
        """element: the piece of UI ('The top'). rule: how a winner is picked ('Highest priority that applies wins')."""
        self.P = project
        self.element = element
        self.rule = rule
        self.rows = []

    def state(self, key, name, priority, when, until, variants, gives_way_to=(), note='', question=None):
        """variants: up to 4 of ('card', img, ref, label) or ('gap', gid, label).
        question: a Q id, or a list of them, still open about this state (shown in amber until decided)."""
        self.rows.append(dict(key=key, name=name, priority=priority, when=when, until=until, variants=variants,
                              gives_way_to=list(gives_way_to), note=note, question=question))

    def _variant(self, v):
        if v[0] == 'card':
            _, img, ref, lab = v
            return (f'<div style="width:{CARD_W}px;height:{CARD_H}px;background:#FFFFFF;border:1px solid {LINE};border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;box-sizing:border-box;flex-shrink:0">'
                    f'<img src="paper-asset://{self.P.img_dir}/{img}.png" style="width:{THUMB_W}px;height:{THUMB_H}px;border-radius:8px;border:1px solid {LINE};object-fit:cover;flex-shrink:0" />'
                    + t(ref, 10, 13, 700, MUTED, 'letter-spacing:0.06em;padding:0 2px;') + t(lab, 12, 15, 700, INK, 'padding:0 2px;') + '</div>')
        _, gid, lab = v
        g = self.P.gap(gid)
        return (f'<div style="width:{CARD_W}px;height:{CARD_H}px;background:#FBFBFA;border:1.5px dashed #B4BDBF;border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;box-sizing:border-box;flex-shrink:0">'
                f'<div style="width:{THUMB_W}px;height:{THUMB_H}px;flex-shrink:0;border-radius:8px;background:#F1F3F3;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px;padding:10px;box-sizing:border-box">'
                + t('NEEDS DESIGN', 9, 11, 700, AMBER, 'letter-spacing:0.08em;') + t(g['need'], 11, 15, 500, MUTED, 'text-align:center;') + '</div>'
                + t(gid, 10, 13, 700, AMBER, 'letter-spacing:0.06em;padding:0 2px;') + t(lab, 12, 15, 700, INK, 'padding:0 2px;') + '</div>')

    def _row(self, r, y, W, max_var):
        names = {x['key']: x['name'] for x in self.rows}
        yields = ', '.join(names.get(k, k) for k in r['gives_way_to']) or 'nothing: it stays until it ends'
        var_w = max_var * CARD_W + (max_var - 1) * VAR_GAP        # same width on every row, so the text column lines up
        q = ''
        qids = r['question'] if isinstance(r['question'], (list, tuple)) else [r['question']] if r['question'] else []
        byid = {x['id']: x for x in self.P.questions()}
        for qid in qids:
            qq = byid.get(qid)
            if qq and qq['state'] != 'decided':
                q += (f'<div style="display:flex;gap:8px;background:#FFF7EA;border-radius:10px;padding:10px 12px">'
                      + t(qid, 13, 18, 700, AMBER, 'white-space:nowrap;') + t(qq['text'], 13, 18, 500, INK) + '</div>')
        facts = ''.join('<div style="display:flex;gap:12px">' + t(k, 12, 18, 700, MUTED, 'width:120px;flex-shrink:0;letter-spacing:0.06em;') + t(v, 15, 21, 500, INK) + '</div>'
                        for k, v in (('SHOWS WHEN', r['when']), ('UNTIL', r['until']), ('GIVES WAY TO', yields)) + ((('NOTE', r['note']),) if r['note'] else ()))
        return (f'<div layer-name="State · {r["name"]}" style="position:absolute;left:{LEFT}px;top:{y}px;width:{W-2*LEFT}px;height:{CARD_H+40}px;background:#FFFFFF;border:1px solid {LINE};border-radius:20px;padding:20px 24px;display:flex;gap:28px;align-items:flex-start;box-sizing:border-box">'
                + f'<div style="width:{PRI_W}px;height:{PRI_W}px;border-radius:{PRI_W//2}px;background:{INK};display:flex;align-items:center;justify-content:center;flex-shrink:0">' + t(str(r['priority']), 24, 28, 700, '#FFFFFF') + '</div>'
                + f'<div style="width:{NAME_W}px;flex-shrink:0;display:flex;flex-direction:column;gap:4px">' + t(r['name'], 22, 27, 700, INK, 'letter-spacing:-0.015em;') + t(f'priority {r["priority"]}', 12, 16, 500, MUTED) + '</div>'
                + f'<div style="display:flex;gap:{VAR_GAP}px;width:{var_w}px;flex-shrink:0">' + ''.join(self._variant(v) for v in r['variants']) + '</div>'
                + f'<div style="flex:1;display:flex;flex-direction:column;gap:12px">{facts}{q}</div></div>')

    def render(self, title, right, story, name):
        rows = sorted(self.rows, key=lambda r: r['priority'])
        max_var = max(len(r['variants']) for r in rows)
        W = 2 * LEFT + 48 + PRI_W + 28 + NAME_W + 28 + max_var * CARD_W + (max_var - 1) * VAR_GAP + 28 + TEXT_W
        y = 300
        B = board.Board(self.P, name)
        B.add('header', f'<div layer-name="Header bar" style="position:absolute;left:40px;top:40px;width:{W-80}px;height:56px;background:{INK};border-radius:14px;display:flex;align-items:center;padding:0 20px;gap:16px;box-sizing:border-box">'
              + t('State map', 13, 18, 500, '#9AA4A6') + '<div style="width:1px;height:20px;background:#3A4245"></div>' + t(title, 17, 22, 700, '#FFFFFF')
              + '<div style="flex:1"></div>' + t(right, 13, 18, 500, '#9AA4A6') + f'<div style="width:10px;height:10px;border-radius:5px;background:{base.ACCENT}"></div></div>')
        B.add('story', f'<div layer-name="Story line" style="position:absolute;left:40px;top:116px;width:{min(W-80, 2600)}px;display:flex;flex-direction:column;gap:10px">'
              + t(story, 17, 24, 500, MUTED) + t(f'Rule: {self.rule}', 17, 24, 700, INK) + '</div>')
        for r in rows:
            B.add('state' + r['key'].replace('_', ''), self._row(r, y, W, max_var))
            y += CARD_H + 40 + ROW_GAP
        print(f'{len(rows)} states · {sum(1 for r in rows for v in r["variants"] if v[0] == "gap")} variants to design')
        return B.emit(W, y + 40)
