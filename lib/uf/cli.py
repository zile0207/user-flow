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
ops <board> [--discard]                 after --drift: the Paper calls for the sync plan, ready to paste
                                        (--discard also deletes the hand-added nodes drift found)
"""
import json, os, re, subprocess, sys
from . import board

STATE_ORDER = ('todo', 'exploring', 'explored', 'promoted', 'later')


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
    lines.append('Master map: ' + ((m.get('artboard') or 'painted') if isinstance(m, dict) else (m or 'not yet')))

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
    lines.append(f"Gaps: {c['todo']} to design · {c['exploring']} exploring · {c['explored']} explored · {c['promoted']} promoted · {c['later']} after MVP")
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


def _val(v):
    try:
        return json.loads(v)
    except ValueError:
        return v


def main(P, argv):
    args = list(argv)
    if not args:
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
        P.set_gap(args[0], **{k: _val(v) for k, v in (a.split('=', 1) for a in args[1:])})
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
    elif cmd == 'add-rule':
        P.add_rule(args[0], args[1])
        print(f"{args[0]} rules: {len(P.cfg['rules'][args[0]])}")
    else:
        print(__doc__)
        sys.exit(2)
