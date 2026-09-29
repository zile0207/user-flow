"""Behaviour tests for sync, drift, the registries and the command line. Run by scripts/test.sh.
Each test works on a fresh temp copy of tests/fixture, so nothing here touches the fixture itself."""
import json, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(REPO, 'tests', 'fixture')
ENV = dict(os.environ, USER_FLOW_ROOT=REPO)
sys.path.insert(0, os.path.join(REPO, 'lib'))


def fresh():
    d = tempfile.mkdtemp()
    shutil.copytree(FIXTURE, os.path.join(d, 'fixture'))
    return os.path.join(d, 'fixture', 'design', 'user-flow')


def run(root, *args, ok=True):
    r = subprocess.run([sys.executable, *args], cwd=os.path.join(root, 'specs'), env=ENV, capture_output=True, text=True)
    if ok and r.returncode:
        raise AssertionError(f'{args} failed:\n{r.stdout}\n{r.stderr}')
    return r.stdout + r.stderr


def plan(root, board):
    return json.load(open(os.path.join(root, 'out', board, 'sync', 'plan.json')))


def ops(p, kind):
    return [o for o in p['ops'] if o['op'] == kind]


def edit(path, old, new):
    s = open(path).read()
    assert old in s, f'{old!r} not in {path}'
    open(path, 'w').write(s.replace(old, new, 1))


def test_commit_then_nothing_to_do():
    root = fresh()
    assert 'paint in full' in run(root, 'journey.py')
    run(root, 'journey.py', '--commit', 'A-0')
    out = run(root, 'journey.py')
    assert '0 insert · 0 replace · 0 move · 0 rename · 0 delete' in out, out


def test_moving_a_node_is_a_move_not_a_replace():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    edit(os.path.join(root, 'specs', 'journey.py'), "m.gap('g3', 1160, Y2", "m.gap('g3', 1200, Y2")
    run(root, 'journey.py')
    p = plan(root, 'journey')
    moved = {o['key'] for o in ops(p, 'move')}
    assert 'g3' in moved, p['ops']
    assert not ops(p, 'insert') and not ops(p, 'delete'), p['ops']
    assert all(o['left'] is not None for o in ops(p, 'move'))


def test_changed_text_is_a_replace_with_its_position():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    edit(os.path.join(root, 'specs', 'journey.py'), "note='Done.'", "note='Done, for now.'")
    run(root, 'journey.py')
    reps = ops(plan(root, 'journey'), 'replace')
    assert [o['key'] for o in reps] == ['s2'], reps
    assert reps[0]['left'] is not None and reps[0]['top'] is not None   # write_html(replace) keeps the old place


def test_legacy_state_upgrades_with_renames():
    """A board committed by 0.2 (format 1: stamped hashes, route-hash edge keys) syncs with renames, not a repaint."""
    import runpy
    from uf import board
    root = fresh()
    specs = os.path.join(root, 'specs')
    captured, maps = {}, []
    orig_add, orig_emit = board.Board.add, board.Board.emit
    def cap(self, key, html):
        k = orig_add(self, key, html); captured[k] = self.body[k]; return k      # as drawn (scaled)
    board.Board.add = cap
    board.Board.emit = lambda self, W, H, page='maps': None
    sys.path.insert(0, specs); argv = sys.argv; sys.argv = ['journey.py']
    try:
        g = runpy.run_path(os.path.join(specs, 'journey.py'), run_name='__main__')
    finally:
        board.Board.add, board.Board.emit = orig_add, orig_emit; sys.argv = argv; sys.path.remove(specs)
    m = g['m']
    old_key = {}
    for ed in m.E:
        k = m._edge_key(ed)
        if k.startswith('e_'):
            ok = 'e' + board.h(repr([(round(x), round(y)) for x, y in ed['p']]))[:8]
            old_key[k] = ok; old_key[k + 'l'] = ok + 'l'
    elements = []
    for k, html in captured.items():
        ok = old_key.get(k, k)
        stamped = html.replace('layer-name="', f'layer-name="journey:{ok} · ', 1)
        elements.append([ok, board.h(stamped.replace(root, '@'))])
    run(root, 'journey.py')
    size = json.load(open(os.path.join(root, 'out', 'journey', 'manifest.json')))['size']
    json.dump({'board': 'journey', 'version': '0.2.0', 'size': size, 'page': 'maps', 'elements': elements, 'artboard': 'A-0'},
              open(os.path.join(root, 'boards', 'journey.json'), 'w'))
    out = run(root, 'journey.py')
    p = plan(root, 'journey')
    renamed = sum(1 for k in old_key if k in captured)
    assert renamed > 0 and len(ops(p, 'rename')) == renamed, (renamed, out)
    assert not ops(p, 'insert') and not ops(p, 'delete') and not ops(p, 'replace') and not ops(p, 'move'), out


def test_drift_reads_tree_summary_and_flags_hand_edits():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    edit(os.path.join(root, 'specs', 'journey.py'), "note='Done.'", "note='Done, for now.'")
    run(root, 'journey.py')
    keys = [e[0] for e in json.load(open(os.path.join(root, 'boards', 'journey.json')))['elements']]
    lines = ['Frame "Journey 1 · Test" (A-0) 1600×2000']
    for i, k in enumerate(keys):
        if k == 'g1':
            continue                                              # deleted by hand
        lines.append(f'  Frame "journey:{k} · something" ({i + 10}B-0) 200×520')
        lines.append('    ... 3 children')
    lines.append('  Text "hand note: check with Mei" (ZZ-0) 120×16')    # added by hand
    tree = os.path.join(root, 'out', 'tree.txt')
    open(tree, 'w').write(json.dumps({'summary': '\n'.join(lines), 'nodeId': 'A-0'}))
    out = run(root, 'journey.py', '--drift', tree)
    assert '1 unkeyed' in out and '1 missing' in out and 'ZZ-0' in out, out
    p = plan(root, 'journey')
    assert ops(p, 'replace')[0]['node'].endswith('B-0') and p['unkeyed'] == ['ZZ-0'], p
    # plain "<id> <name>" lines work too
    open(tree, 'w').write('\n'.join(f'{i + 10}B-0 journey:{k}' for i, k in enumerate(keys)))
    assert '0 unkeyed' in run(root, 'journey.py', '--drift', tree)


def test_drift_refuses_truncated_get_children():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    kids = os.path.join(root, 'out', 'kids.json')
    json.dump({'children': [{'id': f'{i}-0', 'name': f'journey:x{i}'} for i in range(100)]}, open(kids, 'w'))
    r = subprocess.run([sys.executable, 'journey.py', '--drift', kids], cwd=os.path.join(root, 'specs'), env=ENV, capture_output=True, text=True)
    assert r.returncode == 2 and 'get_tree_summary' in r.stdout, r.stdout


def test_commit_output_has_no_stale_plan_line():
    root = fresh()
    out = run(root, 'journey.py', '--commit', 'A-0')
    assert 'paint in full' not in out and 'committed' in out, out


def test_registry_cli():
    root = fresh()
    a = run(root, '_uf.py', 'add-gap', '1', 'Offline at sign-in', 'Say it, keep the typed email.', 'row 2').strip()
    b = run(root, '_uf.py', 'add-gap', '1', 'Offline at sign-in', 'Again.').strip()
    assert a == b, (a, b)                                       # adding twice returns the same gap
    q = run(root, '_uf.py', 'add-question', 'J1', 'Keep the email after an error?', '--blocks', a).strip()
    assert run(root, '_uf.py', 'blocking', a).startswith(q)
    out = run(root, '_uf.py', 'answer', q, '--owner', 'the developers')
    assert '"state": "waiting"' in out and 'decision' not in out, out
    from uf import project
    P = project.load(root)
    items = P.panel('J1', 0, 0, 400)[5]
    assert any('Asked the developers, no answer yet' in tx for _, tx, _ in items), items
    run(root, '_uf.py', 'answer', q, 'Yes, keep it.', '--date', 'Tue 29 Sep')
    assert P.questions()[-1]['state'] == 'decided' and 'owner' not in P.questions()[-1]
    run(root, '_uf.py', 'add-rule', 'copy', 'Say "near you".')
    run(root, '_uf.py', 'add-rule', 'copy', 'Say "near you".')
    cfg = open(os.path.join(root, 'config.json')).read()
    assert cfg.count('Say \\"near you\\".') == 1 and cfg.endswith('\n'), cfg[-80:]
    out = run(root, '_uf.py', 'set-gap', a, 'state="later"', 'on_path=true')
    assert '"state": "later"' in out and '"on_path": true' in out, out


def test_status_is_computed():
    root = fresh()
    out = run(root, '_uf.py', 'status')
    for line in ('Master map:', 'Journeys:', 'Gaps:', 'Questions:', 'Boards out of date:', 'Next up:'):
        assert line in out, out


def test_on_path_marks_gaps_touched_by_the_persona_path():
    root = fresh()
    edit(os.path.join(root, 'specs', 'journey.py'), "m.v('d1', 'g1', label='No'", "m.v('d1', 'g1', 'coral', label='No'")
    run(root, 'journey.py')
    from uf import project
    P = project.load(root)
    assert P.gap('N1·1').get('on_path') is True and not P.gap('N1·3').get('on_path')
    assert 'Next up: N1·1' in run(root, '_uf.py', 'status')


def test_ops_prints_ready_calls():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    edit(os.path.join(root, 'specs', 'journey.py'), "note='Done.'", "note='Done, for now.'")
    edit(os.path.join(root, 'specs', 'journey.py'), "m.gap('g3', 1160, Y2", "m.gap('g3', 1200, Y2")
    run(root, 'journey.py')
    keys = [e[0] for e in json.load(open(os.path.join(root, 'boards', 'journey.json')))['elements']]
    tree = os.path.join(root, 'out', 'tree.txt')
    open(tree, 'w').write('\n'.join([f'{i + 10}B-0 journey:{k}' for i, k in enumerate(keys)] + ['99Z-0 hand note']))
    assert 'ops have no node id' in run(root, '_uf.py', 'ops', 'journey', ok=False)
    run(root, 'journey.py', '--drift', tree)
    out = run(root, '_uf.py', 'ops', 'journey', '--discard')
    assert '"99Z-0"' in out and 'write_html(mode="replace")' in out and '"left": "2600px"' in out and 'update_styles' in out, out


def test_bus_ends_are_keyed_by_their_node():
    root = fresh()
    edit(os.path.join(root, 'specs', 'journey.py'), "if __name__ == '__main__':",
         "m.e([m.c('g3', 'r'), (1500, m.c('g3', 'r')[1]), (1500, 300)], na=True)\n"
         "m.e([(1500, 300), (1600, 300)], na=True, key='bus_top')\nif __name__ == '__main__':")
    run(root, 'journey.py')
    keys = [e[0] for e in json.load(open(os.path.join(root, 'out', 'journey', 'manifest.json')))['elements']]
    assert 'e_g3_bus' in keys and 'e_bus_top' in keys, keys


def test_boards_never_show_images():
    """Screens are live copies of real Paper frames. Only an exploration's references (other apps) may be images."""
    import glob
    root = fresh()
    for spec in ('journey', 'master', 'states', 'promote', 'explore'):
        run(root, f'{spec}.py')
    for board_dir in glob.glob(os.path.join(root, 'out', '*')):
        html = ''.join(open(f).read() for f in glob.glob(os.path.join(board_dir, 'full', '*.html')))
        imgs = re.findall(r'<img [^>]*>', html)
        if os.path.basename(board_dir).startswith('explore'):
            imgs = [i for i in imgs if '/refs/' not in i]
        assert not imgs, (board_dir, imgs[:2])
    html = ''.join(open(f).read() for f in glob.glob(os.path.join(root, 'out', 'journey', 'full', '*.html')))
    assert 'x-paper-clone node-id="S1-0"' in html and 'zoom' not in html          # real size, 1:1
    assert re.search(r'layer-name="Screen" style="position:relative;width:390px;height:844px', html), 'screen box must be the device size'


def test_chunks_hold_few_copies():
    from uf import board
    root = fresh()
    run(root, 'journey.py')
    import glob
    for f in glob.glob(os.path.join(root, 'out', '*', 'full', '*.html')):
        assert open(f).read().count('<x-paper-clone') <= board.CLONE_MAX, f


def test_library_index_find_and_found_gaps():
    root = fresh()
    os.makedirs(os.path.join(root, 'out'), exist_ok=True)
    tree = os.path.join(root, 'out', 'lib.txt')
    open(tree, 'w').write(json.dumps({'summary': '\n'.join([
        ' "" (root_node_p-1-0) ?×?',
        '  Frame "DO4 · Tap Use my location · the phone asks" (PY1-0) 390×844', '    ... 5 children',
        '  Frame "B5 · Auth" (1C5N-0) 390×844',
        '  Frame "5.4 · 7 · The video is private · Decided" (ITS-0) 390×844',
        '  Frame "5.4 · ONE LINK · DECIDED" (BGG-0) 5560×?',
        '  Frame "ROW · MONDAY" (15B0-0) 12530×120'])}))
    assert '3 screens, 2 headers' in run(root, '_uf.py', 'library', tree)
    out = run(root, '_uf.py', 'find', 'video', 'private')
    assert out.strip().startswith('ITS-0'), out
    assert 'ITS-0' in run(root, '_uf.py', 'unplaced', 'journey', '5.4')
    assert 'PY1-0' in run(root, '_uf.py', 'unplaced', 'journey', 'DO')
    from uf.library import ref_of
    assert ref_of('5.4 · 7 · The video is private · Decided') == '5.4·7' and ref_of('DO4 · Tap') == 'DO4' and ref_of('MON b · Page') == 'MON b'
    run(root, '_uf.py', 'set-gap', 'N1·1', 'state=found', 'node=1C5N-0', 'ref=B5')
    run(root, 'journey.py')
    html = ''.join(open(os.path.join(root, 'out', 'journey', 'full', f)).read() for f in sorted(os.listdir(os.path.join(root, 'out', 'journey', 'full'))))
    assert 'node-id="1C5N-0"' in html and 'B5 · WAS N1·1' in html
    assert '1 found in the library' in run(root, '_uf.py', 'status')
    import sys as _s; _s.path.insert(0, os.path.join(root, 'specs'))
    from uf import project, master
    M = master.MasterMap(project.load(root))
    assert M.library_area('Links', '5.4', ['5.4'], gaps=['N1·3']) == 1 and M.areas[0]['items'][0][1] == 'ITS-0'


def test_stale_recopies_on_next_sync():
    root = fresh()
    run(root, 'journey.py'); run(root, 'journey.py', '--commit', 'A-0')
    assert '1 elements will be re-copied' in run(root, '_uf.py', 'stale', 'journey', 'S1')
    out = run(root, 'journey.py')
    assert '1 replace' in out, out


def test_library_layout_moves_frames_and_copies_nothing():
    root = fresh()
    os.makedirs(os.path.join(root, 'out'), exist_ok=True)
    tree = os.path.join(root, 'out', 'lib.txt')
    open(tree, 'w').write('\n'.join([' "" (root_node_p-1-0) ?×?',
        '  Frame "DO4 · Tap Use my location" (PY1-0) 390×844', '  Frame "DO2 · Second open" (Q2R-0) 390×844',
        '  Frame "5.2 · 2 · Scrolled, grouped" (HQ8-0) 390×?', '  Frame "5.4 · ONE LINK" (BGG-0) 5560×?']))
    run(root, '_uf.py', 'library', tree)
    sys.path.insert(0, os.path.join(root, 'specs'))
    from uf import project, library_layout
    L = library_layout.LibraryLayout(project.load(root), cols=2, origin=(1000, 0), per_row=2)
    L.area('Day one', 'DO', ['DO'], gaps=['N1·1'])
    L.area('Explore', '5.2', ['5.2'])
    plan = L.render('Test', 'today')
    assert [m['node'] for m in plan['moves']] == ['Q2R-0', 'PY1-0', 'HQ8-0'], plan['moves']     # natural order, tall frames last
    assert all('x-paper-clone' not in m['html'] and '<img' not in m['html'] for m in plan['made'])
    assert sum(1 for m in plan['made'] if m['name'].startswith('master:gap')) == 1
    out = run(root, '_uf.py', 'layout-ops', 'master')
    assert '"PY1-0"' in out and 'create_artboard' in out


def test_promote_makes_library_frames_then_records_them():
    root = fresh()
    out = run(root, 'promote.py')
    plan = json.load(open(os.path.join(root, 'out', 'promoted_j1', 'promote.json')))
    assert plan['made'] and plan['made'][0]['name'].startswith('X1·1 · ') and plan['made'][0]['width'] == 390
    from uf import project
    assert project.load(root).gap('N1·4')['state'] == 'explored'          # nothing recorded before painting
    nodes = [f'P{i}-0' for i in range(len(plan['made']))]
    run(root, '_uf.py', 'promoted', 'promoted_j1', *nodes)
    g = project.load(root).gap('N1·4')
    assert g['state'] == 'promoted' and g['screen_nodes'] == nodes and g['node'] == nodes[0] and g['screen_ids'][0] == 'X1·1'
    assert 'layer-name="X1·1 · ' in open(plan['made'][0]['file']).read()
    run(root, '_uf.py', 'set-gap', 'N1·4', 'state=explored')                    # back again: promotion fields go
    g = project.load(root).gap('N1·4')
    assert 'screen_nodes' not in g and 'screen_ids' not in g


def test_library_layout_is_incremental():
    root = fresh()
    os.makedirs(os.path.join(root, 'out'), exist_ok=True)
    tree = os.path.join(root, 'out', 'lib.txt')
    open(tree, 'w').write('\n'.join([' "" (root_node_p-1-0) ?×?',
        '  Frame "DO4 · Tap Use my location" (PY1-0) 390×844', '  Frame "DO2 · Second open" (Q2R-0) 390×844']))
    run(root, '_uf.py', 'library', tree)
    sys.path.insert(0, os.path.join(root, 'specs'))
    from uf import project, library_layout
    def layout():
        L = library_layout.LibraryLayout(project.load(root), cols=4, origin=(0, 0), per_row=1)
        L.area('Day one', 'DO', ['DO'], gaps=['N1·1', 'N1·4'])
        return L.render('Test', 'today')
    layout()
    first = run(root, '_uf.py', 'layout-ops', 'master')
    assert '2 frames to move' in first and '(first layout)' in first
    ids = os.path.join(root, 'out', 'ids.txt')
    plan = json.load(open(os.path.join(root, 'out', 'master', 'layout.json')))
    open(ids, 'w').write(''.join(f'M{i}-0 {m["name"]}\n' for i, m in enumerate(plan['made'])))
    run(root, '_uf.py', 'layout-commit', 'master', ids)
    layout()
    assert '0 frames to move · 0 generated frames to delete · 0 to make' in run(root, '_uf.py', 'layout-ops', 'master')
    run(root, '_uf.py', 'set-gap', 'N1·1', 'state=later')                  # one gap changes: only its frame
    layout()
    again = run(root, '_uf.py', 'layout-ops', 'master')
    assert '2 generated frames to delete · 2 to make' in again and '"M1-0", "M2-0"' in again, again      # its frame and the band's count


def test_brief_and_coverage():
    root = fresh()
    os.makedirs(os.path.join(root, 'out'), exist_ok=True)
    tree = os.path.join(root, 'out', 'lib.txt')
    open(tree, 'w').write('\n'.join([' "" (root_node_p-1-0) ?×?', '  Frame "A·1 · Welcome" (S1-0) 390×844',
                                       '  Frame "DO4 · Tap Use my location" (PY1-0) 390×844']))
    run(root, '_uf.py', 'library', tree)
    run(root, 'journey.py')
    cfg = json.load(open(os.path.join(root, 'config.json')))
    cfg['maps']['journeys'] = [{'no': 1, 'name': 'Test', 'spec': 'specs/journey.py'}]
    json.dump(cfg, open(os.path.join(root, 'config.json'), 'w'))
    out = run(root, '_uf.py', 'coverage')
    assert 'NO MAP YET' in out and 'DO' in out, out
    b = run(root, '_uf.py', 'brief')
    for part in ('## Status', '## Gaps', '## Questions', '## Coverage of the library', 'N1·1'):
        assert part in b, part


def test_cross_file_frames_are_real_layers_at_real_size():
    root = fresh()
    cfg = json.load(open(os.path.join(root, 'config.json')))
    cfg['sources']['paper']['library_file_id'] = 'LIBFILE'
    json.dump(cfg, open(os.path.join(root, 'config.json'), 'w'))
    out = run(root, 'journey.py')
    assert 'frames not fetched yet' in out, out
    top = """(
    <div style={{ backgroundColor: '#000000', display: 'flex', flexDirection: 'column', x: '10px' }}>
      <div style={{ backgroundColor: '#E05254', height: '184px', width: '390px' }}>
        <div style={{ color: '#FFFFFF', fontFamily: '"Switzer-Bold", "Switzer"', fontSize: '19px' }}>{'Kok Sen'} for dinner</div>
      </div>
      <div style={{ backgroundColor: '#FFFFFF', borderTopLeftRadius: '32px', height: '660px', width: '390px' }} />
    </div>
  )"""
    fill = """(
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ backgroundColor: '#FFFFFF', borderTopLeftRadius: '32px', height: '700px', width: '390px' }}>
        <div style={{ fontSize: 28, fontWeight: 700 }}>Explore</div>
        <svg width="24" height="24" viewBox="0 0 24 24"><path d="M1 1" strokeWidth="2" /></svg>
      </div>
    </div>
  )"""
    fd = os.path.join(root, 'frames'); os.makedirs(fd, exist_ok=True)
    open(os.path.join(fd, 'S1-0.jsx'), 'w').write(top)
    open(os.path.join(fd, 'S2-0.jsx'), 'w').write(fill)
    edit(os.path.join(root, 'specs', 'journey.py'), "ref='A·1', title='Welcome', note='First screen.', jamie=True)",
         "ref='A·1', title='Welcome', note='First screen.', jamie=True, sheet='S2-0')")
    out = run(root, 'journey.py')
    html = ''.join(open(os.path.join(root, 'out', 'journey', 'full', f)).read() for f in sorted(os.listdir(os.path.join(root, 'out', 'journey', 'full'))))
    assert 'x-paper-clone' not in html and '<img' not in html
    assert 'Kok Sen for dinner' in html and 'Explore' in html                  # the top, over the fill's sheet
    assert 'stroke-width="2"' in html and 'x:10px' not in html
    assert 'font-size:19px' in html and 'font-size:28px' in html               # real size, not scaled with the board
    assert 'height:660px' in html                                              # cut to the empty sheet's height
    assert re.search(r'layer-name="Screen" style="position:relative;width:390px;height:844px', html)


def test_frames_page_types_each_screen_once_then_boards_clone_it():
    root = fresh()
    cfg = json.load(open(os.path.join(root, 'config.json')))
    cfg['sources']['paper'].update(library_file_id='LIBFILE', frames_page='p-9-0')
    json.dump(cfg, open(os.path.join(root, 'config.json'), 'w'))
    out = run(root, 'journey.py')
    assert 'not on the Frames page yet' in out, out
    assert 'frames to fetch' in run(root, '_uf.py', 'frames-local', 'journey')
    fd = os.path.join(root, 'frames'); os.makedirs(fd, exist_ok=True)
    for n in ('S1-0', 'S2-0', 'X12A-0'):
        open(os.path.join(fd, f'{n}.jsx'), 'w').write("(<div style={{ backgroundColor: '#000000' }}><div style={{ fontSize: '19px' }}>" + n + "</div></div>)")
    listing = run(root, '_uf.py', 'frames-local', 'journey')
    assert 'copy:S1-0 · ' in listing and 'copy:S2-0 · ' in listing and 'create_artboard' in listing, listing
    open(os.path.join(root, 'out', 'ids.txt'), 'w').write('L1-0 copy:S1-0 · A·1\nL2-0 copy:S2-0 · A·2\nL3-0 copy:X12A-0 · N1·2\n')
    run(root, '_uf.py', 'frames-local-commit', os.path.join(root, 'out', 'ids.txt'))
    out = run(root, 'journey.py')
    assert 'not on the Frames page' not in out, out
    html = ''.join(open(os.path.join(root, 'out', 'journey', 'full', f)).read() for f in sorted(os.listdir(os.path.join(root, 'out', 'journey', 'full'))) if f.endswith('.html'))
    assert 'node-id="L1-0"' in html and 'node-id="L2-0"' in html and 'zoom' not in html
    paint = json.load(open(os.path.join(root, 'out', 'journey', 'full', 'paint.json')))
    first = open(os.path.join(root, 'out', 'journey', 'full', paint['parallel'][0])).read()
    assert paint['parallel'] and paint['serial'] and 'layer-name="Screen"' in first


if __name__ == '__main__':
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            try:
                fn(); print(f'{name}: ok')
            except Exception as e:
                fails += 1; print(f'{name}: FAIL\n  {type(e).__name__}: {e}')
    sys.exit(1 if fails else 0)
