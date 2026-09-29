"""The project's command line, so every agent reads and writes the registries the same way.

    python3 design/user-flow/specs/_uf.py <command> …

status                                  the status block the router prints (renders every spec to check sync)
gaps [--state todo] [--map J1]          gaps, grouped by map; persona's-path gaps first
questions [--state open] [--map J1]     questions, grouped by map
blocking <gap id>                       open questions that block a gap
add-gap <journey no> <title> <need> [<where>]
set-gap <gap id> key=value …            numbers and true/false are JSON, anything else is text
add-question <map id> <text> [--blocks N1·2,N1·3] [--about <text>]
answer <q id> [<decision>] [--owner <who>] [--date <date>]
add-rule copy|product <text>
library <tree file>                     index the library page: get_tree_summary(root_node_<page>, depth 1), saved
find <words…> | --gap <gap id>          library screens that match (confirm each with a screenshot)
unplaced <board> <group,group…>         library screens in those groups that the board doesn't show yet
stale <board> <node id…> | all          copies of these frames get re-copied on the next sync (after the source changed)
layout-ops <board>                      the Paper calls that lay the library page out as the master map (only what changed)
layout-commit <board> [<tree or ids>]  record the layout; give the page's tree (or "<id> <name>" lines) so generated frames have ids
promoted <board> <node id…>             after promote-design's frames are made: record their ids and nodes
brief                                   a compact digest of the whole project, for answering questions about it
coverage                                which library screen families each journey shows, and which no journey covers yet
screens [--area X] [--group MON] [--find words] [--top-only]
                                        the screen index: every library screen, its area, stop and whether it's top-only
frames <board>                          frames a board needs from the library file that aren't fetched yet (cross-file)
frames-save <node id> <file>            store one get_jsx(inline-styles) result in the frame cache
frames-from-transcript <jsonl>          store every get_jsx result found in a Claude Code session transcript
frames-local <board>                    the copies to make on the Frames page for a board (each screen typed once)
frames-local-commit <tree or id lines>  record the Frames page copies (names start "copy:"), so boards clone them
tree <saved tool result> <out file>     turn a get_tree_summary result (even the harness's saved JSON) into "<id> <name>" lines
bind-from-transcript <jsonl>            store every get_tree_summary and get_jsx result on the library file from a session
bind-read <frame> <tree file> <jsx file> store one frame's two reads (the harness's saved results work as they are)
bind-plan <batch> <frame…> | --board <b> the update_styles payloads that bind these frames to the design tokens
          [--file <file id>]            (out/bind/<batch>/NN.json), what stays literal, and which frames are fully bound
bind-check <file id> <card node…>        pasted copies on a board: is every value in each copied screen a token?
bind-status [<board>]                   how many library frames are bound to tokens; with a board, which of its aren't
ops <board> [--discard]                 after --drift: the Paper calls for the sync plan, ready to paste
                                        (--discard also deletes the hand-added nodes drift found)
"""
import json, os, re, subprocess, sys
from . import board
from .base import nid as board_nid

STATE_ORDER = ('todo', 'exploring', 'found', 'explored', 'promoted', 'later')


def _opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


def _gkey(g):
    m = re.match(r'N(\d+)·(\d+)', g['id'])
    return (int(m.group(1)), int(m.group(2))) if m else (999, 0)


def _boards(P):
    """(label, spec path, artboard) for every board recorded in config.json → maps."""
    maps = P.cfg.get('maps', {})
    out = []
    m = maps.get('master')
    if isinstance(m, dict) and m.get('spec'):
        out.append(('master', m['spec'], m.get('artboard')))
    elif isinstance(m, str):
        out.append(('master', 'specs/master.py', m))
    for kind in ('journeys', 'flows', 'states', 'explorations', 'promoted'):
        for e in maps.get(kind, []) or []:
            if e.get('spec'):
                label = {'journeys': f"J{e.get('no', '')}", 'flows': f"F{e.get('no', '')}",
                         'explorations': f"explore {e.get('gap', '')}"}.get(kind, e.get('name') or e['spec'])
                out.append((label, e['spec'], e.get('artboard')))
    return out


def _render(P, spec):
    path = os.path.join(P.root, spec)
    if not os.path.exists(path):
        return None, f'missing spec {spec}'
    r = subprocess.run([sys.executable, path], cwd=os.path.dirname(path), capture_output=True, text=True)
    if r.returncode:
        return None, (r.stderr.strip().splitlines() or ['failed'])[-1]
    return r.stdout, None


def status(P):
    cfg = P.cfg
    gaps = P.gaps()
    persona = cfg.get('persona', {}).get('name', 'the persona')
    lines = [f"{cfg.get('project', 'Project')} · user-flow"]
    m = cfg.get('maps', {}).get('master')
    paper = cfg.get('sources', {}).get('paper', {})
    if isinstance(m, dict) and m.get('layout') == 'library':
        master = f"the library, laid out by area on {paper.get('library_page_name') or m.get('page')}"
    elif isinstance(m, dict):
        master = m.get('artboard') or 'painted'
    else:
        master = m or 'not yet'
    lines.append('Master map: ' + master)

    out_of_date, rendered = [], {}
    for label, spec, art in _boards(P):
        out, err = _render(P, spec)
        rendered[spec] = out or ''
        if err:
            out_of_date.append(f'{label} ({err})')
            continue
        sync = next((l for l in out.splitlines() if 'sync:' in l), '')
        if 'paint in full' in sync:
            out_of_date.append(f'{label} (not painted yet)')
        elif any(int(n) for n in re.findall(r'(\d+) (?:insert|replace|move|rename|delete)', sync)) or 'size changed' in sync:
            out_of_date.append(f"{label} ({sync.split('sync:')[1].strip()})")
    gaps = P.gaps()           # rendering journeys refreshes on_path

    def counts_line(e):
        out = rendered.get(e.get('spec'), '')
        m_ = re.search(r'designed (\d+) · to design (\d+)', out)
        return f"{m_.group(1)} designed · {m_.group(2)} to design" if m_ else 'not rendered'
    js = cfg.get('maps', {}).get('journeys', [])
    lines.append('Journeys: ' + (' · '.join(f"{e['no']} {e['name']} ({counts_line(e)})" for e in js) or 'none'))
    fl = cfg.get('maps', {}).get('flows', [])
    lines.append('Flows: ' + (' · '.join(f"F{e.get('no', '?')} {e.get('job') or e.get('name', '')}" for e in fl) or 'none'))
    st = cfg.get('maps', {}).get('states', [])
    lines.append('States: ' + (' · '.join(e.get('element') or e.get('name') or e.get('spec', '') for e in st) or 'none'))
    c = {s: sum(1 for g in gaps if g.get('state', 'todo') == s) for s in STATE_ORDER}
    lines.append(f"Gaps: {c['todo']} to design · {c['exploring']} exploring · {c['found']} found in the library · {c['explored']} explored · {c['promoted']} promoted · {c['later']} after MVP")
    lib = P.cfg.get('sources', {}).get('paper', {}).get('library_page')
    if lib and not os.path.exists(os.path.join(P.root, 'library.json')):
        lines.append('Library: not indexed yet · run `_uf.py library` (see project-and-paper.md → The library)')
    qs = P.questions()
    lines.append(f"Questions: {sum(q['state'] == 'open' for q in qs)} open · {sum(q['state'] == 'waiting' for q in qs)} waiting on someone")
    lines.append('Boards out of date: ' + (', '.join(out_of_date) or 'none'))

    order = {f"J{e['no']}": i for i, e in enumerate(js)}
    todo = sorted((g for g in gaps if g.get('state', 'todo') == 'todo'), key=lambda g: (order.get(g.get('map'), 99), _gkey(g)))
    on_path = [g for g in todo if g.get('on_path')]
    pool, note = (on_path, '') if on_path else (todo, f" (no open gap on {persona}'s path; first open gap)")
    nxt = next((g for g in pool if not P.blocking(g['id'])), None)
    blocked = [g for g in pool[:pool.index(nxt)]] if nxt else pool
    if nxt:
        s = f"Next up: {nxt['id']} {nxt['title']}{note}"
        if blocked:
            s += ' · skipped ' + ', '.join(f"{g['id']} (waits on {', '.join(q['id'] for q in P.blocking(g['id']))})" for g in blocked)
        lines.append(s)
    else:
        lines.append('Next up: nothing to design' if not todo else 'Next up: every open gap waits on a question · run answer-questions')
    pinned = cfg.get('plugin_version')
    if pinned and pinned != board.VERSION:
        lines.append(f'Note: set up with user-flow {pinned}, running {board.VERSION}. The next sync of each board may show changes.')
    print('\n'.join(lines))


def list_gaps(P, args):
    state = _opt(args, '--state'); mp = _opt(args, '--map')
    gaps = [g for g in P.gaps() if (not state or g.get('state', 'todo') == state) and (not mp or g.get('map') == mp)]
    names = {f"J{e['no']}": e['name'] for e in P.cfg.get('maps', {}).get('journeys', [])}
    for mp_ in sorted({g.get('map', '?') for g in gaps}, key=lambda m: (len(m), m)):
        print(f"{mp_} · {names.get(mp_, '')}".rstrip(' ·'))
        for g in sorted((g for g in gaps if g.get('map') == mp_), key=lambda g: (not g.get('on_path'), _gkey(g))):
            bits = [g.get('state', 'todo')]
            if g.get('on_path'): bits.append('on the path')
            if g.get('where'): bits.append(g['where'])
            bl = P.blocking(g['id'])
            if bl: bits.append('waits on ' + ', '.join(q['id'] for q in bl))
            print(f"  {g['id']}  {g['title']}  ({' · '.join(bits)})")


def list_questions(P, args):
    state = _opt(args, '--state'); mp = _opt(args, '--map')
    qs = [q for q in P.questions() if (not state or q['state'] == state) and (not mp or q['map'] == mp)]
    for mp_ in sorted({q['map'] for q in qs}, key=lambda m: (len(m), m)):
        print(mp_)
        for q in (q for q in qs if q['map'] == mp_):
            tag = {'open': '', 'waiting': f" (waiting on {q.get('owner', 'someone')})", 'decided': ' (decided)'}[q['state']]
            print(f"  {q['id']}{tag}  {q['text']}")
            if q.get('decision'):
                print(f"        → {q['decision']}")


def ops(P, args):
    discard = '--discard' in args
    args = [a for a in args if a != '--discard']
    name = args[0]
    path = os.path.join(P.root, 'out', name, 'sync', 'plan.json')
    plan = json.load(open(path))
    if plan['mode'] != 'sync':
        print(f'{name}: paint in full (out/{name}/full), see sync.md → First paint'); return
    fid = P.cfg.get('sources', {}).get('paper', {}).get('file_id', '<file id>')
    art = plan.get('artboard')
    by = lambda k: [o for o in plan['ops'] if o['op'] == k]
    if any(o.get('node') is None for o in plan['ops'] if o['op'] != 'insert'):
        print('Run --drift first: some ops have no node id yet (or their element is gone: paint in full).'); sys.exit(2)
    step = 0
    def head(s):
        nonlocal step; step += 1; print(f'\n{step}. {s}')
    dels = [o['node'] for o in by('delete')] + (plan.get('unkeyed', []) if discard else [])
    if dels:
        head('delete_nodes')
        print(json.dumps({'fileId': fid, 'nodeIds': dels}, ensure_ascii=False))
    if by('rename'):
        head('rename_nodes')
        print(json.dumps({'fileId': fid, 'updates': [{'nodeId': o['node'], 'name': o['name']} for o in by('rename')]}, ensure_ascii=False))
    reps = by('replace')
    if reps:
        head(f'replace: {len(reps)} × write_html(mode="replace"), one per line: <node id> <file> <left> <top>'
             + (' · 7 or more: give these lines to the replace subagent (sync.md)' if len(reps) >= 7 else ''))
        for o in reps:
            print(f"{o['node']} {os.path.join(P.root, 'out', name, 'sync', o['file'])} {o.get('left')} {o.get('top')}")
    moves = by('move')
    if moves or reps:
        head('update_styles: the moves below, plus one entry per replaced element (its NEW node id, the left/top above)')
        print(json.dumps({'fileId': fid, 'updates': [{'nodeIds': [o['node']], 'styles': {'left': f"{o['left']}px", 'top': f"{o['top']}px"}} for o in moves]}, ensure_ascii=False))
    ins = by('insert')
    if ins:
        head(f'insert: write_html(mode="insert-children", targetNodeId="{art}") with each file')
        for o in ins:
            print(os.path.join(P.root, 'out', name, 'sync', o['file']))
    if plan.get('size_changed'):
        head('artboard size: update_styles')
        W, H = plan['size']
        print(json.dumps({'fileId': fid, 'updates': [{'nodeIds': [art], 'styles': {'width': f'{W}px', 'height': f'{H}px'}}]}))
    if not step:
        print('nothing to paint')
    print(f'\nThen: screenshot the changed nodes at scale 1, and `python3 specs/<spec>.py --commit {art}`.')


def _layout_state(P, name):
    os.makedirs(os.path.join(P.root, 'boards'), exist_ok=True)
    p = os.path.join(P.root, 'boards', f'{name}_layout.json')
    return (json.load(open(p)) if os.path.exists(p) else None), p


def layout_ops(P, name):
    """The Paper calls for the library layout: only what changed since the last layout-commit."""
    out = os.path.join(P.root, 'out', name)
    plan = json.load(open(os.path.join(out, 'layout.json')))
    state, _ = _layout_state(P, name)
    fid = P.cfg.get('sources', {}).get('paper', {}).get('file_id', '<file id>')
    page = plan['page']
    made_dir = os.path.join(out, 'made')
    os.makedirs(made_dir, exist_ok=True)
    for f in os.listdir(made_dir):
        os.remove(os.path.join(made_dir, f))
    old_moves = (state or {}).get('moves', {})
    old_made = (state or {}).get('made', {})
    moves = [m for m in plan['moves'] if old_moves.get(m['node']) != [m['left'], m['top']]]
    new_made = {m['name']: m for m in plan['made']}
    gone = [(n, v.get('node')) for n, v in old_made.items() if n not in new_made or new_made[n]['h'] != v['h']]
    make = [m for m in plan['made'] if m['name'] not in old_made or old_made[m['name']]['h'] != m['h']]
    print(f"{name}: {len(moves)} frames to move · {len(gone)} generated frames to delete · {len(make)} to make"
          + ('' if state else ' (first layout)'))
    if not state:
        print(f"1. First layout: get_tree_summary(root_node_{page}, depth 1) and delete any child whose name starts with \"{plan['prefix']}\".")
    elif gone:
        ids = [nid for _, nid in gone if nid]
        print('1. delete_nodes (generated frames that changed or went away):')
        print(json.dumps({'fileId': fid, 'nodeIds': ids}))
        missing = [n for n, nid in gone if not nid]
        if missing:
            print('   no node id recorded for: ' + '; '.join(missing) + ' (find them by name)')
    if plan.get('from_page') and plan['from_page'] != page and not state:
        print(f"\n1b. Move the library frames to page {page} (ids stay the same): move_nodes, in batches of 100:")
        for i in range(0, len(moves), 100):
            print(json.dumps({'fileId': fid, 'nodes': [{'nodeId': m['node'], 'parentId': f'root_node_{page}'} for m in moves[i:i + 100]]}))
    for i in range(0, len(moves), 100):
        print(f"\n2.{i // 100 + 1} update_styles (move frames {i + 1}–{min(i + 100, len(moves))} of {len(moves)}):")
        print(json.dumps({'fileId': fid, 'updates': [{'nodeIds': [m['node']], 'styles': {'left': f"{m['left']}px", 'top': f"{m['top']}px"}} for m in moves[i:i + 100]]}, ensure_ascii=False))
    if make:
        print(f"\n3. Make {len(make)} frames: create_artboard(fileId, pageId \"{page}\", name, width, height, backgroundColor transparent), "
              "then write_html(insert-children, the new artboard, the file). Note each new id.")
        for j, m in enumerate(make):
            f = os.path.join(made_dir, f'{j:02d}.html'); open(f, 'w').write(m['html'])
            print(f"  {m['name']} | {m['width']} x {m['height']} | left {m['left']} top {m['top']} | {f}")
        print("\n4. One update_styles with every made frame's left/top (create_artboard ignores position).")
    print(f"\nThen: _uf.py layout-commit {name} <file with one line per made frame: \"<node id> <name>\">")


def layout_commit(P, name, ids_file=None):
    plan = json.load(open(os.path.join(P.root, 'out', name, 'layout.json')))
    state, path = _layout_state(P, name)
    old = (state or {}).get('made', {})
    ids = {}
    if ids_file:                             # "<node id> <name>" lines, or the page's tree summary: only "master:" names count
        rows, _ = board.Board.read_tree(ids_file)
        ids = {nm.strip(): nid_ for nid_, nm in rows if nm.strip().startswith(plan['prefix'])}
    made = {}
    for m in plan['made']:
        node = ids.get(m['name']) or next((v for k, v in ids.items() if m['name'].startswith(k) or k.startswith(m['name'][:45])), None)
        if not node and m['name'] in old and old[m['name']]['h'] == m['h']:
            node = old[m['name']].get('node')
        made[m['name']] = {'h': m['h'], 'node': node}
    st = {'page': plan['page'], 'moves': {m['node']: [m['left'], m['top']] for m in plan['moves']}, 'made': made}
    json.dump(st, open(path, 'w'), indent=1, ensure_ascii=False)
    missing = [n for n, v in made.items() if not v['node']]
    print(f"committed: boards/{name}_layout.json · {len(st['moves'])} frames · {len(made)} generated frames"
          + (f" · no node id for {len(missing)}: when one of them changes, layout-ops can't delete it by id. "
             f"Pass the page's tree (or \"<id> <name>\" lines for the {plan['prefix']} frames) to record them." if missing else ''))


def promoted(P, name, nodes):
    plan = json.load(open(os.path.join(P.root, 'out', name, 'promote.json')))
    assert len(nodes) == len(plan['made']), f"give {len(plan['made'])} node ids, one per made frame, in order"
    by_gap = {}
    for m, n in zip(plan['made'], nodes):
        by_gap.setdefault(m['gap'], []).append((m['id'], board_nid(n)))
    for gid, pairs in by_gap.items():
        P.set_gap(gid, state='promoted', chapter=plan['chapter'], screen_ids=[s for s, _ in pairs],
                  screen_nodes=[n for _, n in pairs], node=pairs[0][1])
        print(f"{gid}: promoted as {', '.join(s for s, _ in pairs)}")
    from .library import Library, ref_of, _group
    L = Library(P)
    if L.data is not None:
        have = {s['node'] for s in L.data['screens']}
        for m, n in zip(plan['made'], nodes):
            n = board_nid(n)
            if n not in have:
                L.data['screens'].append({'node': n, 'name': m['name'], 'ref': m['id'], 'group': _group(m['id']),
                                          'title': m['name'].split(' · ', 1)[-1], 'w': str(m['width']), 'h': str(m['height'])})
        with open(L.path, 'w') as f:
            json.dump(L.data, f, indent=1, ensure_ascii=False); f.write('\n')
        print(f"library.json: added {len(nodes)} frames (no re-index needed)")
    print('Next: re-render and sync the maps that show these gaps, and re-run the master layout.')


def _board_nodes(P, board_name):
    import glob
    html = ''.join(open(f).read() for f in sorted(glob.glob(os.path.join(P.root, 'out', board_name, 'full', '*.html'))))
    return set(re.findall(r'x-paper-clone node-id="([^"]+)"', html))


def _master_areas(P):
    """group → area name, from specs/master.py (library layout or master map), if it exists."""
    import runpy
    path = os.path.join(P.root, 'specs', 'master.py')
    if not os.path.exists(path):
        return {}
    argv = sys.argv
    sys.argv = ['master.py']
    sys.path.insert(0, os.path.dirname(path))
    try:
        g = runpy.run_path(path, run_name='not_main')
    finally:
        sys.argv = argv
    M = g.get('M')
    out = {}
    for a in getattr(M, 'areas', []):
        for grp in a.get('groups', []):
            out.setdefault(grp, a['name'])
        for it in a.get('items', []):
            grp = it.get('group') if isinstance(it, dict) else None
            if grp:
                out.setdefault(grp, a['name'])
    return out


def coverage(P, quiet=False):
    """Library screen families × journeys: what each journey shows, and what no journey covers yet."""
    from .library import Library
    L = Library(P)
    if not L.data:
        print('No library.json: run `_uf.py library` first.'); return {}
    js = P.cfg.get('maps', {}).get('journeys', []) + P.cfg.get('maps', {}).get('flows', [])
    shown = {}
    for e in js:
        name = os.path.basename(e['spec'])[:-3]
        for n in _board_nodes(P, name):
            shown.setdefault(n, []).append(f"J{e['no']}" if e in P.cfg['maps'].get('journeys', []) else f"F{e['no']}")
    areas = _master_areas(P)
    groups = {}
    for s_ in L.screens():
        g = groups.setdefault(s_['group'], {'total': 0, 'shown': 0, 'maps': set()})
        g['total'] += 1
        if s_['node'] in shown:
            g['shown'] += 1
            g['maps'].update(shown[s_['node']])
    claimed = {grp for e in js for grp in e.get('library_groups', [])}
    if not quiet:
        print('Library families (group · area): screens on a map / screens in the library · maps')
        for grp, g in sorted(groups.items(), key=lambda kv: (areas.get(kv[0], 'zz'), kv[0])):
            where = ', '.join(sorted(g['maps'])) or ('claimed, not drawn yet' if grp in claimed else 'NO MAP YET')
            print(f"  {grp:6} · {areas.get(grp, '?'):34} {g['shown']:3} / {g['total']:3} · {where}")
        todo = [grp for grp, g in groups.items() if not g['maps']]
        print(f"\n{len(todo)} of {len(groups)} families appear on no map: {', '.join(sorted(todo))}")
    return groups


def brief(P):
    cfg = P.cfg
    paper = cfg.get('sources', {}).get('paper', {})
    per = cfg.get('persona', {})
    print(f"# {cfg.get('project')} · user-flow brief")
    print(f"Persona: {per.get('name')} · {per.get('summary', '')}")
    print(f"Paper: file {paper.get('file_id')} ({paper.get('file_name', '')}) · library {paper.get('library_page_name')} · maps {paper.get('maps_page_name')} · explorations {paper.get('explore_page_name')}")
    print('\n## Status'); status(P)
    maps = cfg.get('maps', {})
    print('\n## Maps')
    for e in maps.get('journeys', []):
        print(f"- J{e['no']} {e['name']} · {e.get('spec')} · artboard {e.get('artboard', 'not painted')} · library groups {', '.join(e.get('library_groups', [])) or '—'}")
    for e in maps.get('flows', []):
        print(f"- F{e.get('no')} {e.get('job') or e.get('name')} · {e.get('spec')}")
    for e in maps.get('states', []):
        print(f"- States · {e.get('element')} · {e.get('spec')}")
    for e in maps.get('explorations', []):
        print(f"- Explore {e['gap']} · {e.get('state')} {e.get('chosen') or ''} · {e.get('spec')}")
    print('\n## Gaps (to design first: on the persona\'s path, then not blocked)')
    for g in sorted(P.gaps(), key=lambda g: (g.get('state', 'todo') != 'todo', not g.get('on_path'), _gkey(g))):
        bl = ', '.join(q['id'] for q in P.blocking(g['id']))
        extra = ' · on the path' if g.get('on_path') else ''
        extra += f' · waits on {bl}' if bl else ''
        extra += f" · {g.get('ref') or ''}{' ' + g['node'] if g.get('node') else ''}" if g.get('state') in ('found', 'explored', 'promoted') else ''
        print(f"- {g['id']} [{g.get('state', 'todo')}] {g['title']}: {g['need']}{extra}")
    print('\n## Questions')
    for q in P.questions():
        if q['state'] != 'decided':
            print(f"- {q['id']} [{q['state']}{' · ' + q['owner'] if q.get('owner') else ''}] {q['text']}")
    dec = [q for q in P.questions() if q['state'] == 'decided']
    if dec:
        print('Decided: ' + ' · '.join(f"{q['id']} {q.get('decision', '')}" for q in dec))
    print('\n## Rules')
    for k in ('product', 'copy'):
        for r in cfg.get('rules', {}).get(k, []):
            print(f'- ({k}) {r}')
    print('\n## Coverage of the library')
    groups = coverage(P, quiet=True)
    if groups:
        todo = sorted(grp for grp, g in groups.items() if not g['maps'])
        print(f"{sum(g['shown'] for g in groups.values())} of {sum(g['total'] for g in groups.values())} library screens are on a map. "
              f"Families on no map yet: {', '.join(todo) or 'none'}. Run `_uf.py coverage` for the table.")


TOP_FAMILIES = {'GATE', 'N', 'PRE', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'F'}


def _stop(name):
    n = name.lower()
    if '— half' in n or ' half' in n.split('·')[-1]:
        return 'Half'
    if ' page' in n or 'page ·' in n or n.split(' · ')[1:2] == ['page']:
        return 'Page'
    return 'widget'


def screens(P, args):
    """The screen index: what each library frame is, before anyone fetches it."""
    from .library import Library
    L = Library(P)
    if not L.data:
        print('No library.json: run `_uf.py library` first.'); return
    area = _opt(args, '--area'); grp = _opt(args, '--group'); find = _opt(args, '--find')
    top_only = '--top-only' in args
    areas = _master_areas(P)
    used = {}
    for e in P.cfg.get('maps', {}).get('journeys', []) + P.cfg.get('maps', {}).get('flows', []):
        for n in _board_nodes(P, os.path.basename(e['spec'])[:-3]):
            used.setdefault(n, []).append(os.path.basename(e['spec'])[:-3])
    hits = L.find(find, limit=40) if find else None
    rows = [s for _, _, s in hits] if hits else L.screens()
    print('ref · stop · area · kind · used on · node · name')
    for s in rows:
        a = areas.get(s['group'], '?')
        t_only = s['group'] in TOP_FAMILIES
        if (area and area.lower() not in a.lower()) or (grp and s['group'] != grp) or (top_only and not t_only):
            continue
        kind = 'top only (sheet empty: fill with sheet=)' if t_only else 'full screen'
        print(f"{s['ref']:10} · {_stop(s['name']):6} · {a:30} · {kind:41} · {','.join(used.get(s['node'], [])) or '-':10} · {s['node']:7} · {s['name']}")


def _frames_dir(P):
    d = os.path.join(P.root, 'frames')
    os.makedirs(d, exist_ok=True)
    return d


def frames(P, board_name):
    need = os.path.join(P.root, 'out', board_name, 'frames_needed.txt')
    todo = [l.strip() for l in open(need)] if os.path.exists(need) else []
    have = set(f[:-4] for f in os.listdir(_frames_dir(P)))
    todo = [n for n in todo if n not in have]
    fid = P.library_file_id
    if not todo:
        print(f'{board_name}: every frame it needs is in the cache.'); return
    print(f"{board_name}: {len(todo)} frames to fetch from the library file {fid}.")
    print(f"For each: get_jsx(fileId \"{fid}\", nodeId, format \"inline-styles\"), then store it:")
    print("  Claude Code: `_uf.py frames-from-transcript <this session's .jsonl>` stores them all at once, no retyping.")
    print("  Otherwise: save each result to a file and `_uf.py frames-save <node id> <file>`.")
    print('Nodes: ' + ' '.join(todo))


def frames_save(P, node, path):
    raw = open(path).read()
    open(os.path.join(_frames_dir(P), f'{board_nid(node)}.jsx'), 'w').write(raw[raw.find('('):] if '(' in raw else raw)
    print(f'saved {board_nid(node)}')


def frames_from_transcript(P, path):
    uses, n = {}, 0
    for line in open(path):
        if 'get_jsx' not in line and 'tool_result' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        c = d.get('message', {}).get('content')
        if not isinstance(c, list):
            continue
        for x in c:
            if x.get('type') == 'tool_use' and str(x.get('name', '')).endswith('get_jsx'):
                inp = x.get('input', {})
                if inp.get('fileId') in (None, P.library_file_id):
                    uses[x['id']] = inp.get('nodeId')
            elif x.get('type') == 'tool_result' and x.get('tool_use_id') in uses:
                cont = x.get('content')
                t_ = ''.join(y.get('text', '') for y in cont) if isinstance(cont, list) else str(cont)
                if '(' in t_ and '<' in t_:
                    open(os.path.join(_frames_dir(P), f'{board_nid(uses[x["tool_use_id"]])}.jsx'), 'w').write(t_[t_.find('('):])
                    n += 1
    print(f'{n} frames stored in {os.path.relpath(_frames_dir(P), P.root)}/')


def _local_path(P):
    return os.path.join(P.root, 'frames_local.json')


def frames_local(P, board_name):
    from . import base as B
    need_p = os.path.join(P.root, 'out', board_name, 'local_needed.json')
    if not os.path.exists(need_p):
        print(f'{board_name}: every screen it shows is on the Frames page (or render it first).'); return
    need = json.load(open(need_p))
    fd = _frames_dir(P)
    missing = sorted({n for pair in need.values() for n in pair if n and not os.path.exists(os.path.join(fd, f'{n}.jsx'))})
    if missing:
        print(f"{len(missing)} frames to fetch from the library file first: get_jsx(fileId \"{P.library_file_id}\", nodeId, "
              f"format \"inline-styles\"), then `_uf.py frames-from-transcript <session .jsonl>` (or frames-save).")
        print('Nodes: ' + ' '.join(missing)); return
    local = json.load(open(_local_path(P))) if os.path.exists(_local_path(P)) else {}
    page = P.cfg['sources']['paper'].get('frames_page')
    out = os.path.join(P.root, 'out', 'frames_local')
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    lib = {s['node']: s for s in json.load(open(os.path.join(P.root, 'library.json')))['screens']} if os.path.exists(os.path.join(P.root, 'library.json')) else {}
    start = len(local)
    rows = []
    for j, (key, (node, sheet)) in enumerate(sorted(need.items())):
        html = B._frame_html(node, sheet)
        # a last, empty child: if it's on the canvas, the whole copy arrived (frames-local-commit checks it)
        html = html[:html.rindex('</')] + f'<div layer-name="end:{key}" style="width:0px;height:0px;flex-shrink:0"></div>' + html[html.rindex('</'):]
        name = f"copy:{key} · {lib.get(node, {}).get('name', node)}" + (f" + sheet of {lib.get(sheet, {}).get('ref', sheet)}" if sheet else '')
        h = lib.get(node, {}).get('h', '844')
        h = int(float(h)) if h not in ('?', None, '') else 844
        i = start + j
        left, top = (i % 20) * 430, (i // 20) * 3300
        f = os.path.join(out, f'{j:02d}.html'); open(f, 'w').write(html)
        rows.append((name, h, left, top, f))
    print(f"{board_name}: {len(rows)} copies to make on the Frames page ({page}). Each is a real copy of a Master frame, typed once;")
    print("boards then show them as same-file live copies. Ask the user whether to use subagents: if yes, split the list across at most 3")
    print("paste subagents at once (model sonnet: copies are 10-25 KB and must be pasted whole; smaller models cut them short); if no, one at a time:")
    print(f"for each line: create_artboard(fileId, pageId \"{page}\", name, width 390px, height, backgroundColor #FFFFFF), then write_html(insert-children, that artboard, the file, byte for byte).")
    for r in rows:
        print(f"  {r[0]} | 390 x {r[1]} | left {r[2]} top {r[3]} | {r[4]}")
    print("Then one update_styles with each new artboard's left/top, and `_uf.py frames-local-commit <get_tree_summary(root_node_<Frames page>, depth 3)>`:")
    print("it records the copies and names any that arrived incomplete (no end: marker), to delete and make again.")


def frames_local_commit(P, path):
    rows, _ = board.Board.read_tree(path)
    text = board.tree_data(open(path).read())
    text = text if isinstance(text, str) else ''
    ends = set(re.findall(r'"end:([^"]+)"', text))
    deep = bool(re.search(r'^ {6}\S', text, re.M))          # a depth-3 tree shows the end: markers
    local = json.load(open(_local_path(P))) if os.path.exists(_local_path(P)) else {}
    n, bad = 0, []
    for nid_, name in rows:
        name = name.strip()
        if name.startswith('copy:'):
            key = name[5:].split(' · ')[0].strip()
            if deep and key not in ends:
                bad.append((nid_, name)); continue
            local[key] = {'id': nid_, 'name': name}
            n += 1
    if bad:
        print(f'{len(bad)} copies arrived incomplete (no end: marker). Delete them and make them again:')
        for nid_, name in bad:
            print(f'  {nid_}  {name}')
    elif not deep:
        print('(no depth-3 tree given: copies were recorded without checking they arrived whole)')
    with open(_local_path(P), 'w') as f:
        json.dump(local, f, indent=1, ensure_ascii=False); f.write('\n')
    print(f'frames_local.json: {n} copies recorded ({len(local)} in all). Render the board again: its cards are now live copies.')


# ---------- design tokens: bind library frames (tokens.py) ----------

def _bind_dir(P, *parts):
    d = os.path.join(P.root, 'out', 'bind', *parts)
    os.makedirs(d if not os.path.splitext(d)[1] else os.path.dirname(d), exist_ok=True)
    return d


def _tokens_path(P):
    src = P.cfg.get('sources', {}).get('paper', {}).get('tokens', {}).get('source')
    if not src:
        return None
    for base_ in (os.path.dirname(os.path.dirname(P.root)), P.root):
        if os.path.exists(os.path.join(base_, src)):
            return os.path.join(base_, src)
    return None


def _bound_path(P):
    return os.path.join(P.root, 'bound.json')


def _board_frames(P, name):
    d = os.path.join(P.root, 'out', name)
    out = json.load(open(os.path.join(d, 'frames.json'))) if os.path.exists(os.path.join(d, 'frames.json')) else []
    if os.path.exists(os.path.join(d, 'frames_needed.txt')):
        out += [l.strip() for l in open(os.path.join(d, 'frames_needed.txt')) if l.strip()]
    if os.path.exists(os.path.join(d, 'local_needed.json')):
        out += [n for pair in json.load(open(os.path.join(d, 'local_needed.json'))).values() for n in pair if n]
    if os.path.exists(os.path.join(d, 'clones.json')):
        out += [n for ns in json.load(open(os.path.join(d, 'clones.json'))).values() for n in ns]
    from . import base as B
    lib = set(B.FRAME_NAMES) or None
    seen = []
    for n in out:
        n = board_nid(n)
        if n not in seen and (lib is None or n in lib):
            seen.append(n)
    return seen


def bind_read(P, frame, tree_path, jsx_path):
    from .tokens import frame_nodes, result_text
    frame = board_nid(frame)
    tr, jx = result_text(open(tree_path).read()), result_text(open(jsx_path).read())
    nodes, bad = frame_nodes(tr, jx)
    open(os.path.join(_bind_dir(P, 'read'), f'{frame}.tree'), 'w').write(tr)
    open(os.path.join(_bind_dir(P, 'read'), f'{frame}.jsx'), 'w').write(jx)
    print(f'{frame}: {len(nodes)} layers paired' + (f' · {len(bad)} parts did not line up: {bad[:3]}' if bad else ''))


def bind_from_transcript(P, path):
    """Every get_tree_summary / get_jsx result on the library file in a session, newest last, into out/bind/read/."""
    uses, n = {}, 0
    rd = _bind_dir(P, 'read')
    for line in open(path, errors='ignore'):
        if 'get_tree_summary' not in line and 'get_jsx' not in line and 'tool_result' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        c = d.get('message', {}).get('content')
        if not isinstance(c, list):
            continue
        for x in c:
            name = str(x.get('name', ''))
            if x.get('type') == 'tool_use' and (name.endswith('get_tree_summary') or name.endswith('get_jsx')):
                inp = x.get('input', {})
                if inp.get('nodeId') and inp.get('format', 'inline-styles') == 'inline-styles':
                    other = inp.get('fileId') not in (None, P.library_file_id)
                    uses[x['id']] = (board_nid(inp['nodeId']), 'tree' if name.endswith('get_tree_summary') else 'jsx', inp.get('fileId') if other else None)
            elif x.get('type') == 'tool_result' and x.get('tool_use_id') in uses:
                cont = x.get('content')
                t_ = ''.join(y.get('text', '') for y in cont if isinstance(y, dict)) if isinstance(cont, list) else str(cont)
                m = re.search(r'saved to:? (/\S+?\.(?:txt|json))', t_)
                if m and os.path.exists(m.group(1)):
                    from .tokens import result_text
                    t_ = result_text(open(m.group(1)).read())
                node, kind, other = uses[x['tool_use_id']]
                if (kind == 'tree' and '"summary"' in t_) or (kind == 'jsx' and '(' in t_ and '<' in t_):
                    if other:                             # another file (a journey board): kept apart, for bind-check
                        open(os.path.join(_bind_dir(P, 'read', other), f'{node}.{kind}'), 'w').write(t_)
                        n += 1
                        continue
                    open(os.path.join(rd, f'{node}.{kind}'), 'w').write(t_)
                    if kind == 'jsx':                     # the newest read is also the frame cache copies are made from
                        open(os.path.join(_frames_dir(P), f'{node}.jsx'), 'w').write(t_[t_.find('}(') + 1:] if '}(' in t_ else t_[t_.find('('):])
                    n += 1
    print(f'{n} reads stored in {os.path.relpath(rd, P.root)}/ (get_jsx results also refresh the frame cache)')


def bind_plan(P, args):
    from .tokens import Tokens, plan
    fid = _opt(args, '--file', P.library_file_id)
    board_name = _opt(args, '--board')
    batch = args.pop(0) if args else board_name
    frames = [board_nid(a) for a in args] or (_board_frames(P, board_name) if board_name else [])
    tp = _tokens_path(P)
    if not tp:
        print('No token file: set config.json → sources.paper.tokens.source (e.g. "design/tokens.json").'); sys.exit(2)
    if not frames:
        print('No frames: name them, or --board <board> (render the board first).'); sys.exit(2)
    rd = _bind_dir(P, 'read')
    have = {f: (open(os.path.join(rd, f'{f}.tree')).read(), open(os.path.join(rd, f'{f}.jsx')).read())
            for f in frames if os.path.exists(os.path.join(rd, f'{f}.tree')) and os.path.exists(os.path.join(rd, f'{f}.jsx'))}
    missing = [f for f in frames if f not in have]
    if missing:
        print(f'{len(missing)} of {len(frames)} frames not read yet. For each, one call at a time: '
              f'get_tree_summary(fileId "{fid}", nodeId, depth 30) and get_jsx(fileId "{fid}", nodeId, format "inline-styles"); '
              'then `_uf.py bind-from-transcript <session .jsonl>` (or bind-read). Frames: ' + ' '.join(missing))
        if not have:
            sys.exit(2)
    T = Tokens(tp)
    out = _bind_dir(P, batch)
    for f in os.listdir(out):
        if f.endswith('.json'):
            os.remove(os.path.join(out, f))
    per, bound = {}, json.load(open(_bound_path(P))) if os.path.exists(_bound_path(P)) else {}
    for f, pair in have.items():
        c, r = plan(T, {f: pair})
        per[f] = (sum(len(e['nodeIds']) for ch in c for e in ch), r)
    chunks, rep = plan(T, have)
    for i, ch in enumerate(chunks):
        json.dump(ch, open(os.path.join(out, f'{i:02d}.json'), 'w'))
    k = rep['counts']
    print(f"{batch}: {k['frames']} frames · {k['nodes']} layers to bind ({k['values']} values) · {k['bound_already']} values already bound")
    for f, (n, r) in per.items():
        if r['bad']:
            print(f'  {f}: parts did not line up, skipped: {r["bad"][:3]} (read it again; if it persists, bind those parts by hand)')
        elif n == 0:
            bound[f] = {'left': sum(len(v) for v in r['left'].values())}
    json.dump(bound, open(_bound_path(P), 'w'), indent=1, sort_keys=True)
    done = [f for f in have if f in bound and per[f][0] == 0 and not per[f][1]['bad']]
    if done:
        print(f'  fully bound: {len(done)} of {len(have)} ({" ".join(done[:12])}{" …" if len(done) > 12 else ""}), recorded in bound.json')
    if rep['left']:
        print('No token for these (add a token or a snap to the token file, or a keep entry, then plan again):')
        for (kind, v), ids in sorted(rep['left'].items(), key=lambda x: -len(x[1])):
            print(f'  {kind:<13} {v:<28} {len(ids):>4} layers  e.g. {" ".join(ids[:3])}')
    if chunks:
        print(f'{len(chunks)} update_styles calls, one at a time, each with fileId "{fid}" and updates = the file\'s JSON as it is:')
        for i, ch in enumerate(chunks):
            print(f'  {os.path.relpath(os.path.join(out, f"{i:02d}.json"), P.root)}  ({len(json.dumps(ch)) // 1000} KB, {sum(len(e["nodeIds"]) for e in ch)} layers)')
        print('Then read each frame again with get_jsx only (the tree does not change), run bind-from-transcript, and plan again: 0 to bind means done.')


def bind_check(P, args):
    """Pasted copies on a board (another file): is every value in each copied screen a token?"""
    from .tokens import Tokens, read_jsx, copy_root, check
    fid = args.pop(0)
    T = Tokens(_tokens_path(P))
    d = os.path.join(P.root, 'out', 'bind', 'read', fid)
    bad = 0
    for node in [board_nid(a) for a in args]:
        p = os.path.join(d, f'{node}.jsx')
        if not os.path.exists(p):
            print(f'{node}: not read yet: get_jsx(fileId "{fid}", nodeId "{node}", format "inline-styles"), then bind-from-transcript'); bad += 1; continue
        found = check(T, copy_root(read_jsx(open(p).read())))
        if not found:
            print(f'{node}: every value is a token'); continue
        bad += 1
        print(f'{node}: {sum(found.values())} values are not tokens')
        for (what, v, prop), n in sorted(found.items(), key=lambda x: -x[1]):
            print(f'    {n:>3} × {prop}: {v}  ({what})')
    print('all copies tagged' if not bad else f'{bad} of {len(args)} copies need attention')


def bind_status(P, args):
    bound = json.load(open(_bound_path(P))) if os.path.exists(_bound_path(P)) else {}
    from . import base as B
    lib = list(B.FRAME_NAMES)
    print(f'Tokens: {len([n for n in lib if n in bound]) if lib else len(bound)} of {len(lib) or "?"} library frames bound')
    if args:
        fr = _board_frames(P, args[0])
        todo = [f for f in fr if f not in bound]
        print(f'{args[0]}: {len(fr) - len(todo)} of {len(fr)} frames bound' + (f' · to bind: {" ".join(todo)}' if todo else ''))


def _val(v):
    try:
        return json.loads(v)
    except ValueError:
        return v


def main(P, argv):
    args = list(argv)
    if not args:
        if sys.argv[0].endswith('_uf.py'):
            print(__doc__)
        return
    cmd = args.pop(0)
    if cmd == 'status':
        status(P)
    elif cmd == 'gaps':
        list_gaps(P, args)
    elif cmd == 'questions':
        list_questions(P, args)
    elif cmd == 'blocking':
        for q in P.blocking(args[0]):
            print(f"{q['id']}  {q['text']}")
    elif cmd == 'add-gap':
        print(P.add_gap(int(args[0]), args[1], args[2], args[3] if len(args) > 3 else ''))
    elif cmd == 'set-gap':
        P.gap(args[0])
        fields = {k: _val(v) for k, v in (a.split('=', 1) for a in args[1:])}
        if fields.get('state') in ('todo', 'exploring', 'explored', 'later'):
            gs = P.gaps()                      # moving back from promoted: drop what promotion added
            for g in gs:
                if g['id'] == args[0]:
                    for k in ('chapter', 'screen_ids', 'screen_nodes'):
                        g.pop(k, None)
            P.save_gaps(gs)
            for e in P.cfg.get('maps', {}).get('explorations', []):
                if e.get('gap') == args[0] and e.get('state') == 'promoted':
                    e['state'] = 'confirmed'
            P.save_cfg()
        P.set_gap(args[0], **fields)
        print(json.dumps(P.gap(args[0]), ensure_ascii=False))
    elif cmd == 'add-question':
        blocks = _opt(args, '--blocks'); about = _opt(args, '--about', '')
        print(P.add_question(args[0], args[1], about, blocks.split(',') if blocks else ()))
    elif cmd == 'answer':
        owner = _opt(args, '--owner'); date = _opt(args, '--date', '')
        P.answer(args[0], args[1] if len(args) > 1 else None, date, owner)
        print(json.dumps([q for q in P.questions() if q['id'] == args[0]][0], ensure_ascii=False))
    elif cmd == 'ops':
        ops(P, args)
    elif cmd == 'layout-ops':
        layout_ops(P, args[0])
    elif cmd == 'layout-commit':
        layout_commit(P, args[0], args[1] if len(args) > 1 else None)
    elif cmd == 'promoted':
        promoted(P, args[0], args[1:])
    elif cmd == 'screens':
        screens(P, args)
    elif cmd == 'frames':
        frames(P, args[0])
    elif cmd == 'frames-save':
        frames_save(P, args[0], args[1])
    elif cmd == 'frames-local':
        frames_local(P, args[0])
    elif cmd == 'frames-local-commit':
        frames_local_commit(P, args[0])
    elif cmd == 'frames-from-transcript':
        frames_from_transcript(P, args[0])
    elif cmd == 'bind-read':
        bind_read(P, args[0], args[1], args[2])
    elif cmd == 'bind-from-transcript':
        bind_from_transcript(P, args[0])
    elif cmd == 'bind-plan':
        bind_plan(P, args)
    elif cmd == 'bind-check':
        bind_check(P, args)
    elif cmd == 'bind-status':
        bind_status(P, args)
    elif cmd == 'brief':
        brief(P)
    elif cmd == 'coverage':
        coverage(P)
    elif cmd == 'tree':
        rows, _ = board.Board.read_tree(args[0])
        open(args[1], 'w').write(''.join(f'{i} {n}\n' for i, n in rows))
        print(f'{len(rows)} children → {args[1]}')
    elif cmd in ('library', 'find', 'unplaced'):
        from .library import Library
        L = Library(P)
        if cmd == 'library':
            n, hd = L.build(args[0])
            print(f'library.json: {n} screens, {hd} headers and bands')
        elif cmd == 'find':
            if not L.data:
                print('No library.json yet: run `_uf.py library <tree file>` first.'); sys.exit(2)
            gid = _opt(args, '--gap')
            q = ' '.join(args)
            if gid:
                g = P.gap(gid); q = f"{g['title']} {g['need']} {q}"
            for score, hit, s in L.find(q):
                print(f"{s['node']:>8}  {s['name']}   ({', '.join(hit)})")
        else:
            for s in L.unplaced(args[0], set(args[1].split(','))):
                print(f"{s['node']:>8}  {s['name']}")
    elif cmd == 'stale':
        name = args.pop(0)
        clones = json.load(open(os.path.join(P.root, 'out', name, 'clones.json')))
        want = None if args == ['all'] else {board_nid(a) for a in args}
        keys = [k for k, ns in clones.items() if want is None or want & set(ns)]
        sp = os.path.join(P.root, 'boards', f'{name}.json')
        st = json.load(open(sp))
        for e in st['elements']:
            if e[0] in keys:
                e[1] = e[2] = 'stale'
        json.dump(st, open(sp, 'w'), indent=1)
        print(f'{len(keys)} elements will be re-copied on the next sync of {name}')
    elif cmd == 'add-rule':
        P.add_rule(args[0], args[1])
        print(f"{args[0]} rules: {len(P.cfg['rules'][args[0]])}")
    else:
        print(__doc__)
        sys.exit(2)
