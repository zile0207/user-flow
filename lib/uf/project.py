"""A project's user-flow folder: config, gap registry, paths. Created by the init skill.

<app repo>/design/user-flow/
  config.json      sources, theme, persona, rules, maps (see references/project-and-paper.md)
  gaps.json        every needs-design gap: the single source of truth for ids, text and state
  questions.json   every open question and decision, per map: the panels render from it
  boards/          what is painted on each Paper board (written by `--commit`), for sync
  ui_kit.py        the app's own screen parts, copied from its confirmed screens (for explorations)
  specs/           one file per map or exploration: master.py, j1.py, f1.py, explore_n2_1.py …
  library.json     index of the library page (every confirmed screen), from `_uf.py library`
  refs/            reference images from other apps, for explorations (gitignored). Screens are never images.
  out/             rendered chunks (gitignored)
"""
import json, os, re
from . import base

HOME = os.path.join('design', 'user-flow')


def find(start):
    """Walk up from a file or folder to the nearest design/user-flow/config.json."""
    p = os.path.abspath(start)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    while True:
        for cand in (p, os.path.join(p, HOME)):
            if os.path.isfile(os.path.join(cand, 'config.json')) and os.path.basename(cand) == 'user-flow':
                return cand
        parent = os.path.dirname(p)
        if parent == p:
            raise FileNotFoundError('No design/user-flow/config.json above ' + start + '. Run the init skill first.')
        p = parent


class Project:
    def __init__(self, root):
        self.root = root
        self.cfg = json.load(open(os.path.join(root, 'config.json')))
        th = self.cfg.get('theme', {})
        base.set_theme(th.get('accent'), th.get('font'), tuple(th['device']) if th.get('device') else None)
        paper = self.cfg.get('sources', {}).get('paper', {})
        self.library_file_id = paper.get('library_file_id') or paper.get('file_id')
        base.CROSS_FILE = self.library_file_id != paper.get('file_id')
        base.FRAMES_DIR = os.path.join(root, 'frames')
        base.LOCAL_MODE = bool(base.CROSS_FILE and paper.get('frames_page'))
        lp = os.path.join(root, 'frames_local.json')
        base.LOCAL = {k: v['id'] for k, v in json.load(open(lp)).items()} if os.path.exists(lp) else {}
        lib = os.path.join(root, 'library.json')
        if os.path.exists(lib):
            base.FRAME_NAMES = {s['node']: s['name'] for s in json.load(open(lib)).get('screens', [])}
        self.refs_dir = os.path.join(root, 'refs')
        self.specs_dir = os.path.join(root, 'specs')
        for d in (self.refs_dir, os.path.join(root, 'out')):
            os.makedirs(d, exist_ok=True)

    def out(self, name):
        return os.path.join(self.root, 'out', name)

    # ---------------- gap registry
    def _gaps_path(self):
        return os.path.join(self.root, 'gaps.json')

    def gaps(self):
        p = self._gaps_path()
        return json.load(open(p))['gaps'] if os.path.exists(p) else []

    def save_gaps(self, gaps):
        def key(g):
            m = re.match(r'N(\d+)·(\d+)', g['id'])
            return (int(m.group(1)), int(m.group(2))) if m else (999, 0)
        with open(self._gaps_path(), 'w') as f:
            json.dump({'gaps': sorted(gaps, key=key)}, f, indent=2, ensure_ascii=False)
            f.write('\n')

    def gap(self, gid):
        for g in self.gaps():
            if g['id'] == gid:
                return g
        raise KeyError(gid + ' is not in gaps.json')

    def next_gap_id(self, map_no):
        """Gap ids are N<map_no>·<n>, never renumbered: the next id is max + 1 for that map."""
        ns = [int(g['id'].split('·')[1]) for g in self.gaps() if g['id'].startswith(f'N{map_no}·')]
        return f'N{map_no}·{max(ns, default=0) + 1}'

    def add_gap(self, map_no, title, need, where=''):
        """Adds a gap and returns its id. Safe to run twice: a gap with the same map and title is returned, not added again.
        Run it once from the shell (`python3 specs/_uf.py add-gap …`), never inside a spec."""
        gs = self.gaps()
        for g in gs:
            if g.get('map') == f'J{map_no}' and g['title'].strip().lower() == title.strip().lower():
                return g['id']
        gid = self.next_gap_id(map_no)
        gs.append({'id': gid, 'map': f'J{map_no}', 'title': title, 'need': need, 'where': where, 'state': 'todo'})
        self.save_gaps(gs)
        return gid

    def set_gap(self, gid, **fields):
        gs = self.gaps()
        for g in gs:
            if g['id'] == gid:
                g.update(fields)
        self.save_gaps(gs)

    def g(self, gid):
        """kwargs for Map.gap(...) straight from the registry, so maps never copy gap text by hand."""
        g = self.gap(gid)
        return dict(title=g['title'], need=g['need'], gid=gid, state=g.get('state', 'todo'),
                    chosen=g.get('chosen'), round=g.get('round'), node=g.get('node'), ref=g.get('ref'), screen_ids=g.get('screen_ids'))


    # ---------------- questions and decisions
    def _q_path(self):
        return os.path.join(self.root, 'questions.json')

    def questions(self, map_id=None, state=None):
        p = self._q_path()
        qs = json.load(open(p))['questions'] if os.path.exists(p) else []
        return [q for q in qs if (map_id is None or q['map'] == map_id) and (state is None or q['state'] == state)]

    def _save_q(self, qs):
        with open(self._q_path(), 'w') as f:
            json.dump({'questions': qs}, f, indent=2, ensure_ascii=False)
            f.write('\n')

    @staticmethod
    def _qprefix(map_id):
        return f'Q{map_id[1:]}' if map_id.startswith('J') else f'Q{map_id}'

    def add_question(self, map_id, text, about='', blocks=()):
        """map_id: J1, J2, F1, M (master). Ids are Q<journey>·<n> for journeys (Q2·3), QF1·<n> for flows, QM·<n> for the master.
        State maps have no panel: file their questions under the journey that owns the surface.
        blocks: gap ids that shouldn't be designed until this is answered. Safe to run twice (same map and text)."""
        qs = self.questions()
        for q in qs:
            if q['map'] == map_id and q['text'].strip() == text.strip():
                return q['id']
        pre = self._qprefix(map_id)
        ns = [int(q['id'].split('·')[1]) for q in qs if q['id'].split('·')[0] == pre]
        qid = f'{pre}·{max(ns, default=0) + 1}'
        q = {'id': qid, 'map': map_id, 'text': text, 'about': about, 'state': 'open'}
        if blocks:
            q['blocks'] = list(blocks)
        qs.append(q)
        self._save_q(qs)
        return qid

    def answer(self, qid, decision=None, date='', owner=None):
        """Record a decision. owner: who else must confirm (e.g. 'the developers'); keeps it amber until they do.
        decision=None with an owner: asked, no answer yet."""
        qs = self.questions()
        hit = False
        for q in qs:
            if q['id'] == qid:
                hit = True
                q.update(date=date, state='waiting' if owner else 'decided')
                if decision is not None:
                    q['decision'] = decision
                if owner:
                    q['owner'] = owner
                else:
                    q.pop('owner', None)
        if not hit:
            raise KeyError(qid + ' is not in questions.json')
        self._save_q(qs)

    def blocking(self, gid):
        """Open or waiting questions that block a gap: listed in `blocks`, or naming the gap in their text."""
        return [q for q in self.questions() if q['state'] != 'decided'
                and (gid in q.get('blocks', []) or re.search(rf'(?<![\w·]){re.escape(gid)}(?![\w·]|·\d)', q['text']))]

    # ---------------- config
    def save_cfg(self):
        with open(os.path.join(self.root, 'config.json'), 'w') as f:
            json.dump(self.cfg, f, indent=2, ensure_ascii=False)
            f.write('\n')

    def add_rule(self, kind, text):
        """kind: copy or product. Skips a rule that is already there."""
        rules = self.cfg.setdefault('rules', {}).setdefault(kind, [])
        if text not in rules:
            rules.append(text)
            self.save_cfg()

    def panel(self, map_id, x, y, w):
        """panel_spec for Map.render: open and waiting questions in amber, decisions in grey."""
        qs = self.questions(map_id)
        items = []
        for q in qs:
            if q['state'] == 'decided':
                items.append((q['id'], q['decision'], False))
            elif q['state'] == 'waiting':
                if q.get('decision'):
                    items.append((q['id'], f"{q['decision']} Waiting on {q.get('owner', 'someone')}.", True))
                else:
                    items.append((q['id'], f"{q['text']} Asked {q.get('owner', 'someone')}, no answer yet.", True))
            else:
                items.append((q['id'], q['text'], True))
        n_open = sum(1 for q in qs if q['state'] != 'decided')
        title = 'DECISIONS AND OPEN QUESTIONS' if n_open < len(qs) else 'OPEN QUESTIONS'
        return (x, y, w, title, f'{n_open} still open · answer them with answer-questions', items)


def load(start=None):
    return Project(find(start or os.getcwd()))
