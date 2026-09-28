"""Flow maps (master · journey · flow): a spec of nodes and edges in, Paper HTML chunks out.
Rules: references/nodes-and-layout.md."""
import math
from . import base, board
from .base import t, INK, MUTED, LINE, GREY, AMBER

# ---- the grid (see JOURNEY_TEMPLATE.md · Layout)
CW, CH, TH = 200, 520, 390        # card, and the screen thumbnail inside it
DW = 150                          # diamond
ATTACH = 205                      # a card's arrows attach 205px below its top (middle of the thumbnail)
FIRST_TOP = 380                   # row 1 card top
ROW_PITCH = 700                   # card top to next row's card top
WIDTH = {'card': CW, 'gap': CW, 'dia': DW}


def row_y(n):
    """Attach line of row n (1-based)."""
    return FIRST_TOP + (n - 1) * ROW_PITCH + ATTACH


def row_label_top(n):
    return FIRST_TOP + (n - 1) * ROW_PITCH - 84


class Map:
    def __init__(self, journey_no, project):
        """journey_no: the number used in gap ids (N<no>·<n>). project: from `from _uf import P`."""
        self.J = journey_no
        self.P = project
        self.IMG = project.img_dir
        self.N = {}
        self.E = []

    # ---------------- nodes (y is always the row's attach line)
    def card(self, i, x, y, img, ref, title, note, jamie=False):
        """A designed screen. img = file name in img/ (no .png), ref = User Flow ID like 'E7·5'."""
        self.N[i] = dict(kind='card', x=x, y=y - ATTACH, w=CW, h=CH, img=img, ref=ref, title=title, note=note, jamie=jamie)

    def gap(self, i, x, y, title, need, gid=None, state='todo', later=False, chosen=None, round=None, img=None, screen_ids=None):
        """A screen that needs design. gid = 'N2·3' (stable, never renumber).
        state: todo | exploring | explored (then chosen, round, img) ; later=True for after-MVP."""
        if later: state = 'later'
        self.N[i] = dict(kind='gap', x=x, y=y - ATTACH, w=CW, h=CH, title=title, need=need, gid=gid, state=state, chosen=chosen, round=round, img=img, screen_ids=screen_ids)

    def dia(self, i, cx, y, text, sys=False):
        """A decision. sys=False: the user decides (white). sys=True: Argo or the phone decides (ink)."""
        self.N[i] = dict(kind='dia', x=cx - DW // 2, y=y - DW // 2, w=DW, h=DW, text=text, sys=sys)

    def pill(self, i, x, y, w, text, sub, style, jamie=False):
        """style: start (a journey begins) · exit (continues in another journey) · entry (comes from another step) · jump (↩ back to a far node)."""
        self.N[i] = dict(kind='pill', x=x, y=y - 28, w=w, h=56, text=text, sub=sub, style=style, jamie=jamie)

    def sysbox(self, i, x, y, w, text, sub):
        """Argo working in the background (reading, building, sending)."""
        self.N[i] = dict(kind='sys', x=x, y=y - 36, w=w, h=72, text=text, sub=sub)

    def outside(self, i, x, y, w, text, sub):
        """A step outside Argo (TikTok, Instagram, the share sheet, iOS Settings)."""
        self.N[i] = dict(kind='out', x=x, y=y - 36, w=w, h=72, text=text, sub=sub)

    # ---------------- layout helpers
    def seq(self, y, x, items):
        """Lay nodes left to right on one row. items: (method, id, kwargs, gap_after). Returns the next free x.
        Widths come from the node type, or kwargs['w'] for pills, sys and outside boxes."""
        for method, i, kw, gap in items:
            kw = dict(kw)
            if method == 'dia':
                getattr(self, method)(i, x + DW // 2, y, **kw); w = DW
            else:
                getattr(self, method)(i, x, y, **kw); w = kw.get('w', WIDTH.get(method, CW))
            x += w + gap
        return x

    def under(self, ref_id, y):
        """x for a card or gap centred under another node (use for branches that drop straight down)."""
        return int(self.c(ref_id, 'b')[0] - CW / 2)

    def c(self, n, side):
        d = self.N[n]
        x, y, w, h = d['x'], d['y'], d['w'], d['h']
        cy = y + ATTACH if d['kind'] in ('card', 'gap') else y + h / 2
        cx = x + w / 2
        return {'l': (x, cy), 'r': (x + w, cy), 't': (cx, y), 'b': (cx, y + h)}[side]

    # ---------------- edges
    def e(self, pts, col='grey', dash=False, label=None, lp=None, lw=None, na=False):
        """A routed arrow. pts = orthogonal waypoints. col 'coral' only on Jamie's path. dash = remembered for later / after MVP.
        na=True: no arrowhead (the line merges into another line)."""
        self.E.append(dict(p=[tuple(p) for p in pts], c=col, d=dash, l=label, lp=lp, lw=lw, na=na))

    def h(self, a, b, col='grey', label=None, dash=False, lw=None, lp=None):
        p1 = self.c(a, 'r'); p2 = self.c(b, 'l')
        self.e([p1, (p2[0], p1[1])], col, dash, label, lp, lw)

    def v(self, a, b, col='grey', label=None, dash=False, lw=None, lp=None, up=False):
        if up:
            p1 = self.c(a, 't'); p2 = self.c(b, 'b')
        else:
            p1 = self.c(a, 'b'); p2 = self.c(b, 't')
        self.e([p1, (p1[0], p2[1])], col, dash, label, lp, lw)

    # ---------------- counts
    def counts(self):
        cards = sum(1 for d in self.N.values() if d['kind'] == 'card')
        explored = sum(1 for d in self.N.values() if d['kind'] == 'gap' and d['state'] in ('explored', 'promoted'))
        todo = sum(1 for d in self.N.values() if d['kind'] == 'gap' and d['state'] in ('todo', 'exploring'))
        later = sum(1 for d in self.N.values() if d['kind'] == 'gap' and d['state'] == 'later')
        dias = sum(1 for d in self.N.values() if d['kind'] == 'dia')
        return cards + explored, todo, later, dias

    def check(self):
        """Fail loudly on the mistakes that break a map."""
        gids = [d['gid'] for d in self.N.values() if d['kind'] == 'gap']
        assert all(gids), 'every gap needs a stable gid like N2·3'
        assert len(gids) == len(set(gids)), 'duplicate gap ids'
        boxes = [(k, d) for k, d in self.N.items()]
        for i, (a, da) in enumerate(boxes):
            for b, db in boxes[i + 1:]:
                if da['x'] < db['x'] + db['w'] and db['x'] < da['x'] + da['w'] and da['y'] < db['y'] + db['h'] and db['y'] < da['y'] + da['h']:
                    raise AssertionError(f'overlap: {a} and {b}')
        out = {k: 0 for k, d in self.N.items() if d['kind'] == 'dia'}
        for ed in self.E:
            for k in out:
                d = self.N[k]
                x0, y0 = ed['p'][0]
                if d['x'] - 1 <= x0 <= d['x'] + d['w'] + 1 and d['y'] - 1 <= y0 <= d['y'] + d['h'] + 1:
                    out[k] += 2 if ed['na'] else 1   # a no-head stem feeds a bus that fans out
        lonely = [k for k, n in out.items() if n < 2]
        assert not lonely, f'decisions need 2+ exits: {lonely}'

    def warnings(self, rows):
        """Things a person would spot on the board. Printed, not fatal: fix them in the spec."""
        out = []
        labelled = {n for n, *_ in rows}
        used = set()
        for d in self.N.values():
            mid = d['y'] + (ATTACH if d['kind'] in ('card', 'gap') else d['h'] / 2)
            used.add(max(1, round((mid - row_y(1)) / ROW_PITCH) + 1))
        for n in sorted(used - labelled):
            out.append(f'row {n} has nodes but no row label')
        boxes = []
        for ed in self.E:
            if ed['l']:
                (x, y), w, hh = self._label_box(ed)
                boxes.append((ed['l'], x - w / 2, y - hh / 2, w, hh))
        for i, (la, ax, ay, aw, ah) in enumerate(boxes):
            for lb, bx, by, bw, bh in boxes[i + 1:]:
                if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                    out.append(f'labels overlap: "{la}" and "{lb}"')
            for k, d in self.N.items():         # 2px of slack: a label touching a box edge is fine
                if ax + 2 < d['x'] + d['w'] and d['x'] < ax + aw - 2 and ay + 2 < d['y'] + d['h'] and d['y'] < ay + ah - 2:
                    out.append(f'label "{la}" sits on node {k}')
        return out

    # ---------------- render
    def node_html(self, i, d):
        k = d['kind']
        if k == 'card':
            ref_col = base.ACCENT if d['jamie'] else MUTED
            return (f'<div layer-name="{d["ref"]} · {d["title"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:200px;height:520px;background:#FFFFFF;border:1px solid {LINE};border-radius:16px;padding:10px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
                    f'<img src="paper-asset://{self.IMG}/{d["img"]}.png" style="width:180px;height:390px;border-radius:10px;border:1px solid {LINE};object-fit:cover;flex-shrink:0" />'
                    f'<div style="display:flex;flex-direction:column;gap:3px;padding:0 4px">'
                    + t(d['ref'], 11, 14, 700, ref_col, 'letter-spacing:0.06em;') + t(d['title'], 15, 19, 700, INK) + t(d['note'], 12, 16, 500, MUTED) + '</div></div>')
        if k == 'gap':
            g, st = d['gid'], d['state']
            if st == 'promoted':
                sid = (d.get('screen_ids') or [g])[0]
                return (f'<div layer-name="{sid} · {d["title"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:200px;height:520px;background:#FFFFFF;border:1px solid {LINE};border-radius:16px;padding:10px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
                        f'<img src="paper-asset://{self.IMG}/{d["img"]}.png" style="width:180px;height:390px;border-radius:10px;border:1px solid {LINE};object-fit:cover;flex-shrink:0" />'
                        '<div style="display:flex;flex-direction:column;gap:3px;padding:0 4px">' + t(f'{sid} · FROM {g}', 11, 14, 700, MUTED, 'letter-spacing:0.06em;') + t(d['title'], 15, 19, 700, INK)
                        + t(f'Designed in Explore · {g} ({d["chosen"]}).', 12, 16, 500, MUTED) + '</div></div>')
            if st == 'explored':
                return (f'<div layer-name="{g} · {d["title"]} · explored" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:200px;height:520px;background:#FFFFFF;border:1px solid {LINE};border-radius:16px;padding:10px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
                        f'<div style="position:relative;width:180px;height:390px;flex-shrink:0"><img src="paper-asset://{self.IMG}/{d["img"]}.png" style="width:180px;height:390px;border-radius:10px;border:1px solid {LINE};object-fit:cover" />'
                        f'<div style="position:absolute;left:8px;top:8px;background:{base.ACCENT};border-radius:999px;padding:4px 9px">' + t(f'EXPLORED · {d["chosen"]}', 10, 12, 700, '#FFFFFF', 'letter-spacing:0.08em;') + '</div></div>'
                        '<div style="display:flex;flex-direction:column;gap:3px;padding:0 4px">' + t(g, 11, 14, 700, base.ACCENT, 'letter-spacing:0.06em;') + t(d['title'], 15, 19, 700, INK)
                        + t(f'Chosen: {d["chosen"]}, round {d["round"]}. See Explore · {g}.', 12, 16, 500, MUTED) + '</div></div>')
            if st == 'later':
                tag = f'{g} · AFTER MVP'; bot = tag; tagc, bd, bg = '#6B7678', '#D3D8DA', '#FFFFFF'
            elif st == 'exploring':
                tag = f'{g} · EXPLORING'; bot = f'{g} · EXPLORING, ROUND {d["round"] or 1}'; tagc, bd, bg = AMBER, '#B4BDBF', '#FBFBFA'
            else:
                tag = f'{g} · NEEDS DESIGN'; bot = f'{g} · TO DESIGN'; tagc, bd, bg = AMBER, '#B4BDBF', '#FBFBFA'
            return (f'<div layer-name="To design · {d["title"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:200px;height:520px;background:{bg};border:1.5px dashed {bd};border-radius:16px;padding:10px;display:flex;flex-direction:column;gap:12px;box-sizing:border-box">'
                    f'<div style="width:180px;height:390px;flex-shrink:0;border-radius:10px;background:#F1F3F3;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;padding:20px;box-sizing:border-box">'
                    f'<div style="{base.F}font-size:10px;line-height:12px;font-weight:700;letter-spacing:0.08em;color:{tagc};background:#FFFFFF;border-radius:999px;padding:5px 9px;white-space:nowrap">{tag}</div>'
                    + t(d['need'], 13, 18, 500, MUTED, 'text-align:center;') + '</div>'
                    f'<div style="display:flex;flex-direction:column;gap:3px;padding:0 4px">'
                    + t(bot, 11, 14, 700, tagc, 'letter-spacing:0.06em;') + t(d['title'], 15, 19, 700, INK) + '</div></div>')
        if k == 'dia':
            fill = INK if d['sys'] else '#FFFFFF'; col = '#FFFFFF' if d['sys'] else INK
            return (f'<div layer-name="Decision · {d["text"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:150px;height:150px">'
                    f'<svg width="150" height="150" viewBox="0 0 150 150" style="position:absolute;left:0;top:0"><path d="M75 3 L147 75 L75 147 L3 75 Z" fill="{fill}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/></svg>'
                    f'<div style="position:absolute;left:30px;top:30px;width:90px;height:90px;display:flex;align-items:center;justify-content:center">'
                    + t(d['text'], 13, 16, 700, col, 'text-align:center;') + '</div></div>')
        if k == 'pill':
            st = d['style']
            if st == 'start': bg, bd, tc, sc = INK, f'2px solid {INK}', '#FFFFFF', '#B8C0C2'
            elif st == 'exit': bg, bd, tc, sc = '#FFFFFF', f'2px solid {base.ACCENT if d["jamie"] else INK}', INK, MUTED
            elif st == 'entry': bg, bd, tc, sc = '#F1F3F3', f'1.5px dashed {GREY}', INK, MUTED
            else: bg, bd, tc, sc = '#FFFFFF', '1.5px solid #C9D0D2', INK, MUTED
            return (f'<div layer-name="{st.capitalize()} · {d["text"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:56px;background:{bg};border:{bd};border-radius:28px;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:0 16px;box-sizing:border-box;gap:1px">'
                    + t(d['text'], 13, 17, 700, tc, 'text-align:center;white-space:nowrap;') + t(d['sub'], 11, 14, 500, sc, 'text-align:center;white-space:nowrap;') + '</div>')
        if k == 'sys':
            return (f'<div layer-name="Argo · {d["text"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:72px;background:#EEF1F2;border:1.5px solid {GREY};border-radius:14px;display:flex;flex-direction:column;justify-content:center;padding:0 14px;box-sizing:border-box;gap:2px">'
                    + t('ARGO', 10, 12, 700, MUTED, 'letter-spacing:0.08em;') + t(d['text'], 13, 17, 700, INK) + t(d['sub'], 11, 14, 500, MUTED) + '</div>')
        if k == 'out':
            return (f'<div layer-name="Outside · {d["text"]}" style="position:absolute;left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:72px;background:#FFFFFF;border:1.5px dashed {INK};border-radius:6px;display:flex;flex-direction:column;justify-content:center;padding:0 14px;box-sizing:border-box;gap:2px">'
                    + t('OUTSIDE ARGO', 10, 12, 700, MUTED, 'letter-spacing:0.08em;') + t(d['text'], 13, 17, 700, INK) + t(d['sub'], 11, 14, 500, MUTED) + '</div>')
        raise ValueError(k)

    @staticmethod
    def _trim(pts, a, b):
        pts = list(pts)
        def move(p, q, dist):
            L = math.hypot(q[0] - p[0], q[1] - p[1])
            if L == 0: return p
            return (p[0] + (q[0] - p[0]) / L * dist, p[1] + (q[1] - p[1]) / L * dist)
        if len(pts) >= 2:
            pts[0] = move(pts[0], pts[1], min(a, math.hypot(pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]) / 2))
            pts[-1] = move(pts[-1], pts[-2], min(b, math.hypot(pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]) / 2))
        return pts

    def _at(self, p):
        """The node whose box holds point p (arrows start and end on a box edge), or None."""
        for k, d in self.N.items():
            if d['x'] - 2 <= p[0] <= d['x'] + d['w'] + 2 and d['y'] - 2 <= p[1] <= d['y'] + d['h'] + 2:
                return k
        return None

    def _edge_key(self, ed):
        a, b = self._at(ed['p'][0]), self._at(ed['p'][-1])
        if a and b:
            return f'e_{a}_{b}'
        return 'e' + board.h(repr([(round(x), round(y)) for x, y in ed['p']]))[:8]   # joins a line, not a node

    def _label_box(self, ed):
        lab = ed['l']; lp = ed['lp']
        if not lp:
            (ax, ay), (bx, by) = ed['p'][0], ed['p'][1]; lp = ((ax + bx) / 2, (ay + by) / 2)
        lw = ed['lw'] or max(36, round(len(lab) * 6.6 + 16))
        lines = max(1, math.ceil((len(lab) * 6.6) / (lw - 12)))
        lh = lines * 15 + 6
        return lp, lw, lh

    def edge_html(self, ed):
        """Returns (key, arrow svg, label html or None). The key names the nodes it joins, so it survives moves."""
        pts = ed['p']; col = base.ACCENT if ed['c'] == 'coral' else GREY; sw = 2.5 if ed['c'] == 'coral' else 2
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; pad = 10
        x0, y0 = min(xs) - pad, min(ys) - pad
        w = max(xs) - min(xs) + 2 * pad; hh = max(ys) - min(ys) + 2 * pad
        loc = [(p[0] - x0, p[1] - y0) for p in pts]
        head = ''
        line = loc
        if not ed['na']:
            (ax, ay), (bx, by) = loc[-2], loc[-1]
            L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
            bp = (bx - ux * 10, by - uy * 10); px, py = -uy, ux
            head = f'<path d="M{bx:.1f} {by:.1f} L{bp[0]+px*5.5:.1f} {bp[1]+py*5.5:.1f} L{bp[0]-px*5.5:.1f} {bp[1]-py*5.5:.1f} Z" fill="{col}"/>'
            line = loc[:-1] + [bp]
        halo = self._trim(line, 12, 12)
        dstr = lambda P: 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in P)
        dash = ' stroke-dasharray="6 5"' if ed['d'] else ''
        key = self._edge_key(ed)
        svg = (f'<svg layer-name="Arrow" width="{w:.0f}" height="{hh:.0f}" viewBox="0 0 {w:.0f} {hh:.0f}" style="position:absolute;left:{x0:.0f}px;top:{y0:.0f}px">'
               f'<path d="{dstr(halo)}" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="butt" stroke-linejoin="round"/>'
               f'<path d="{dstr(line)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{dash}/>{head}</svg>')
        lab_html = None
        if ed['l']:
            lab = ed['l']; lp, lw, lh = self._label_box(ed)
            lc = base.ACCENT if ed['c'] == 'coral' else MUTED
            lab_html = (f'<div layer-name="Label · {lab}" style="position:absolute;left:{lp[0]-lw/2:.0f}px;top:{lp[1]-lh/2:.0f}px;width:{lw}px;background:#FFFFFF;border-radius:6px;padding:3px 4px;box-sizing:border-box;display:flex;justify-content:center">'
                        + t(lab, 12, 15, 600, lc, 'text-align:center;') + '</div>')
        return key, svg, lab_html

    def _mark_path(self, P):
        """Record in the registry which gaps the persona's path (a coral arrow) touches. The status "next up" uses it."""
        on = set()
        for ed in self.E:
            if ed['c'] == 'coral':
                on.update(k for k in (self._at(ed['p'][0]), self._at(ed['p'][-1])) if k)
        for k, d in self.N.items():
            if d['kind'] == 'gap' and d['gid']:
                want = k in on
                try:
                    have = P.gap(d['gid']).get('on_path', False)
                except KeyError:
                    continue
                if have != want:
                    P.set_gap(d['gid'], on_path=want)

    def render(self, P, name, W, title, right, story, rows, panel_spec=None, dividers=(), kind='journey'):
        """Paint one map as keyed elements (see board.py). rows: [(row_no, title, sub, persona_path?)].
        panel_spec: (x, y, w, title, sub, items) or P.panel('J2', x, y, w). Returns the sync plan."""
        self.check()
        for w in self.warnings(rows):
            print('  warning:', w)
        if kind == 'journey':
            self._mark_path(P)
        designed, todo, later, dias = self.counts()
        stats = [(str(designed), 'designed screens', INK), (str(todo), 'to design', AMBER)]
        if later: stats.append((str(later), 'after MVP', '#6B7678'))
        stats.append((str(dias), 'decisions', INK))
        B = board.Board(P, name)
        for k, html in header(W, title, right, story, stats,
                              [(row_label_top(n), f'{n} · {tt}', sub, base.ACCENT if jm else INK) for n, tt, sub, jm in rows],
                              self.J, dividers, P.cfg, kind):
            B.add(k, html)
        if panel_spec:
            B.add('panel', panel(*panel_spec))
        for k, d in self.N.items():
            B.add(k, self.node_html(k, d))
        for ed in self.E:
            k, svg, lab = self.edge_html(ed)
            k = B.add(k, svg)
            if lab:
                B.add(k + 'l', lab)
        H = max(d['y'] + d['h'] for d in self.N.values()) + 80
        for ed in self.E:
            H = max(H, max(p[1] for p in ed['p']) + 60)
        if panel_spec:
            H = max(H, panel_spec[1] + 120 + 60 * math.ceil(len(panel_spec[5]) / 2))
        print(f'designed {designed} · to design {todo} · after MVP {later} · decisions {dias} · edges {len(self.E)}')
        return B.emit(W, H)


def header(width, title, right, story, stats, rows, journey_no=None, dividers=(), cfg=None, kind='journey'):
    """Returns keyed elements: header, story, legend, coverage, row<n>, divider<n>."""
    cfg = cfg or {}
    persona = cfg.get('persona', {}).get('name', 'The persona')
    app = cfg.get('project', 'The app')
    screens_name = cfg.get('sources', {}).get('paper', {}).get('screens_page_name', 'the screens page')
    device = cfg.get('device_label', 'Mobile · iPhone')
    bar = (f'<div layer-name="Header bar" style="position:absolute;left:40px;top:40px;width:{width-80}px;height:56px;background:{INK};border-radius:14px;display:flex;align-items:center;padding:0 20px;gap:16px;box-sizing:border-box">'
           + t(device, 13, 18, 500, '#9AA4A6') + '<div style="width:1px;height:20px;background:#3A4245"></div>'
           + t(title, 17, 22, 700, '#FFFFFF') + '<div style="flex:1"></div>' + t(right, 13, 18, 500, '#9AA4A6')
           + f'<div style="width:10px;height:10px;border-radius:5px;background:{base.ACCENT}"></div></div>')
    st = f'<div layer-name="Story line" style="position:absolute;left:40px;top:116px;width:2600px">' + t(story, 17, 24, 500, MUTED) + '</div>'

    def item(g, l): return f'<div style="display:flex;align-items:center;gap:10px">{g}' + t(l, 13, 18, 500, INK, 'white-space:nowrap;') + '</div>'
    def ln(c, dash=False, sw=2):
        d = ' stroke-dasharray="6 5"' if dash else ''
        return f'<svg width="44" height="12" viewBox="0 0 44 12"><path d="M2 6 L34 6" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"{d}/><path d="M43 6 L33 11.5 L33 0.5 Z" fill="{c}"/></svg>'
    def dg(fill): return f'<svg width="20" height="20" viewBox="0 0 20 20"><path d="M10 1.5 L18.5 10 L10 18.5 L1.5 10 Z" fill="{fill}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/></svg>'
    j = journey_no or 1
    items = [item(ln(base.ACCENT, sw=2.5), f"{persona}'s path"), item(ln(GREY), 'Another way through'), item(ln(GREY, True), 'Remembered for later'),
             item(dg('#FFFFFF'), 'The user decides'), item(dg(INK), f'{app} or the phone decides'),
             item('<div style="width:14px;height:20px;border-radius:3px;border:1.5px solid #C9D0D2;background:#FFFFFF"></div>', f'Designed screen (id from {screens_name})'),
             item('<div style="width:14px;height:20px;border-radius:3px;border:1.5px dashed #B4BDBF;background:#F1F3F3"></div>',
                  f'Needs design (N{j}·3 = journey {j}, gap 3)' if kind == 'journey' else 'Needs design (N2·3 = gap 3 of journey 2)'),
             item(f'<div style="width:14px;height:20px;border-radius:3px;border:1px solid #C9D0D2;background:#FFFFFF;position:relative"><div style="position:absolute;left:2px;top:2px;width:8px;height:4px;border-radius:2px;background:{base.ACCENT}"></div></div>', 'Explored and chosen'),
             item('<div style="width:14px;height:20px;border-radius:3px;border:1.5px dashed #D3D8DA;background:#FFFFFF"></div>', 'After MVP'),
             item(f'<div style="width:30px;height:16px;border-radius:5px;border:1.5px solid {GREY};background:#EEF1F2"></div>', f'{app} works in the background'),
             item(f'<div style="width:30px;height:16px;border-radius:3px;border:1.5px dashed {INK};background:#FFFFFF"></div>', f'Outside {app}'),
             item(f'<div style="width:30px;height:14px;border-radius:7px;border:1.5px solid {INK};background:#FFFFFF"></div>', 'Continues in another map'),
             item(f'<div style="width:30px;height:14px;border-radius:7px;border:1.5px dashed {GREY};background:#F1F3F3"></div>', 'Comes from another step')]
    leg = f'<div layer-name="Legend" style="position:absolute;left:40px;top:172px;width:{width-760}px;display:flex;flex-wrap:wrap;align-items:center;column-gap:28px;row-gap:12px">' + ''.join(items) + '</div>'
    stt = (f'<div layer-name="Coverage" style="position:absolute;left:{width-660}px;top:160px;width:620px;display:flex;justify-content:flex-end;gap:36px">'
           + ''.join(f'<div style="display:flex;flex-direction:column;gap:2px;align-items:flex-end">' + t(n, 32, 36, 700, c, 'letter-spacing:-0.02em;') + t(l, 12, 16, 500, MUTED, 'white-space:nowrap;') + '</div>' for n, l, c in stats) + '</div>')
    out = [('header', bar), ('story', st), ('legend', leg), ('coverage', stt)]
    for i, (y, title_, sub, col) in enumerate(rows):
        out.append((f'row{i+1}', f'<div layer-name="Row label" style="position:absolute;left:40px;top:{y}px;display:flex;align-items:baseline;gap:10px">'
                    + t(title_, 12, 16, 700, col, 'letter-spacing:0.08em;white-space:nowrap;') + (t(sub, 13, 16, 500, MUTED, 'white-space:nowrap;') if sub else '') + '</div>'))
    for i, dy in enumerate(dividers):
        out.append((f'divider{i+1}', f'<div layer-name="Divider" style="position:absolute;left:40px;top:{dy}px;width:{width-80}px;height:1px;background:#EEF0F1"></div>'))
    return out


def panel(x, y, w, title, sub, items):
    """Decisions and open questions. items: (num, text, still_open)."""
    half = (len(items) + 1) // 2
    def col(its):
        return '<div style="flex:1;display:flex;flex-direction:column;gap:14px">' + ''.join(
            '<div style="display:flex;gap:12px">' + t(str(n), 15, 21, 700, AMBER if op else MUTED, 'width:auto;flex-shrink:0;white-space:nowrap;') + t(tx, 15, 21, 500, INK if op else MUTED) + '</div>'
            for n, tx, op in its) + '</div>'
    return (f'<div layer-name="Decisions and open questions" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;background:#F6F7F7;border-radius:20px;padding:32px 36px;display:flex;flex-direction:column;gap:20px;box-sizing:border-box">'
            f'<div style="display:flex;align-items:baseline;gap:12px">' + t(title, 12, 16, 700, INK, 'letter-spacing:0.08em;') + t(sub, 13, 16, 500, MUTED) + '</div>'
            f'<div style="display:flex;gap:40px">' + col(items[:half]) + col(items[half:]) + '</div></div>')
