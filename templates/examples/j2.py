"""Journey 2 · Collecting: link -> places -> board."""
from _uf import P
from uf.jmap import Map, row_y

W, H = 5400, 3860
Y1, Y2, Y3, Y4, Y5 = 585, 1285, 1985, 2685, 3385
m = Map(2, P.img_dir)

# ---------------- Row 1 · Jamie's first link
m.pill('e_j1', 40, Y1, 220, 'From 1 · First open', 'the top asks for a link', 'entry')
m.card('a42', 330, Y1, '1D4N', 'A4·2', 'Links, nothing yet', 'Jamie taps the top. It shows how to send the first link.', True)
m.dia('d_clip', 735, Y1, 'Link copied?', sys=True)
m.card('a43', 900, Y1, '1D7N', 'A4·3', 'Paste', 'The Paste card shows. Jamie taps Paste.', True)
m.dia('d_kind', 1255, Y1, 'What kind of link?', sys=True)
m.dia('d_first', 1885, Y1, 'First link?', sys=True)
m.card('a44', 2050, Y1, '1DAQ', 'A4·4', 'Reading, want a ping?', "Argo reads, and asks to tell Jamie when it's done.", True)
m.dia('d_ping', 2405, Y1, "Ping when it's done?")
m.card('a45', 2590, Y1, '1DDS', 'A4·5', 'The phone asks', 'iOS alert for notifications. Jamie taps Allow.', True)
m.sysbox('p_read', 2900, Y1, 180, 'Argo reads it', 'about a minute')
m.dia('d_found', 3235, Y1, 'Found places?', sys=True)
m.dia('d_where', 3495, Y1, 'Still in Argo?', sys=True)
m.card('a46', 3680, Y1, '1DH4', 'A4·6', '7 places, in the top', 'The top opens with the places from the video.', True)
m.dia('d_add', 4035, Y1, 'Add to board or Later?')
m.dia('d_boards', 4305, Y1, 'Any boards yet?', sys=True)
m.card('a52', 4470, Y1, '1DOM', 'A5·2', 'Your first board', 'Jamie keeps 5 of 7 and names it Late-night zi char.', True)
m.card('a53', 4790, Y1, '1DXT', 'A5·3', 'Made, Undo', 'Back on Links. The other 2 wait in Not in a board yet.', True)
m.pill('x_out', 5080, Y1, 250, 'Build a plan now', '→ 4 · Making a plan', 'exit', jamie=True)

m.h('e_j1', 'a42', 'coral', 'Taps the top', lw=64)
m.h('a42', 'd_clip', 'coral', 'Copies a TikTok link, comes back', lw=110)
m.h('d_clip', 'a43', 'coral', 'Yes')
m.h('a43', 'd_kind', 'coral')
m.h('d_kind', 'd_first', 'coral', 'New TikTok or Instagram link', lw=130, lp=(1470, Y1))
m.h('d_first', 'a44', 'coral', 'Yes')
m.h('a44', 'd_ping', 'coral')
m.h('d_ping', 'a45', 'coral', 'Turn on')
m.h('a45', 'p_read', 'coral', 'Either answer', lw=90)
m.h('p_read', 'd_found', 'coral')
m.h('d_found', 'd_where', 'coral', 'Yes, 7', lw=56)
m.h('d_where', 'a46', 'coral', 'Yes')
m.h('a46', 'd_add', 'coral')
m.h('d_add', 'd_boards', 'coral', 'Add to board', lw=96)
m.h('d_boards', 'a52', 'coral', 'No')
m.h('a52', 'a53', 'coral', 'Make board', lw=90)
m.h('a53', 'x_out', 'coral')
# Not now on the ping: over the top lane
m.e([m.c('d_ping', 't'), (2405, 345), (2990, 345), m.c('p_read', 't')], label="Not now · the top says when it's done", lp=(2700, 345), lw=240)

# ---------------- Row 2 · other ways in, and while Argo reads
m.pill('x_plus', 40, Y2, 220, 'From any tab: + → Link', 'the + in the bar', 'entry')
m.card('d42', 330, Y2, '1MB9', 'D4·2', 'The + menu', 'Link, Board or Plan.')
m.card('e61', 635, Y2, '1PT9', 'E6·1', 'Nothing copied', 'Shows how to share from TikTok or Instagram, or copy the link.')
m.outside('ext', 910, Y2, 180, 'In TikTok or Instagram', 'Jamie finds the video')
m.outside('e_share', 1290, Y2, 200, 'Shares the video', 'Share → Argo, Argo closed')
m.gap('g_share', 1540, Y2, **P.g('N2·1'))
m.card('e63', 1785, Y2, '1PZQ', 'E6·3', 'Still reading', 'From the second link on. Jamie can leave, or stop.')
m.dia('d_why', 3235, Y2, 'Why not?', sys=True)
m.dia('d_alerts', 3495, Y2, 'Alerts on?', sys=True)
m.gap('g_push', 3680, Y2, **P.g('N2·2'))

m.h('x_plus', 'd42')
m.e([m.c('d42', 'r'), (600, Y2), (600, Y1)], label='Link', lp=(600, 1000), na=True)
m.v('d_clip', 'e61', label='No', lp=(735, 760))
m.h('e61', 'ext', label='Leaves', lw=50)
m.v('ext', 'a43', up=True, label='Copies the link, comes back', lp=(1000, 990), lw=120)
m.h('e_share', 'g_share')
m.e([m.c('g_share', 't'), (1640, Y1)], label='Reads it', lp=(1640, 990), na=True)
m.v('d_first', 'e63', label='No', lp=(1885, 760))
m.e([m.c('e63', 'r'), (2990, Y2), m.c('p_read', 'b')], label='Argo keeps reading', lp=(2450, Y2), lw=130)
m.v('d_found', 'd_why', label='No', lp=(3235, 760))
m.v('d_where', 'd_alerts', label='No, Jamie left Argo', lp=(3495, 760), lw=100)
m.h('d_alerts', 'g_push', label='On')
m.v('g_push', 'a46', up=True, label='Taps it', lp=(3780, 990))
m.e([m.c('d_alerts', 'b'), (3495, 1640), (3960, 1640), (3960, 1040), (3780, 1040)], label='Off · the top shows it on the next open', lp=(3727, 1640), lw=230, na=True)

# ---------------- Row 3 · when Argo can't read it
m.gap('g_notlink', 1035, Y3, **P.g('N2·3'))
m.gap('g_dup', 1275, Y3, **P.g('N2·4'))
m.gap('g_stop', 1785, Y3, **P.g('N2·5'))
m.card('t_type', 2100, Y3, '1Q6F', 'E6·5', 'Type the place', 'Argo finds it as Jamie types.')
m.card('t_pick', 2400, Y3, '1QBN', 'E6·6', 'After a pick', 'Add 1 place to a board.')
m.card('f_priv', 2655, Y3, '1Q38', 'E6·4', 'The video is private', 'Try again, or type the place in it.')
m.card('f_gone', 2895, Y3, '1QF2', 'E6·7', 'The video is gone', 'Taken down. Type the place, or remove the link.')
m.card('f_none', 3135, Y3, '1QHY', 'E6·8', 'No places in it', 'A recipe, not a place. Type one if there is.')
m.card('f_fail', 3375, Y3, '24MN', 'J3·5', "Couldn't read that link", 'What-if: the top says so. Try again goes back to reading.')
m.card('f_off', 3615, Y3, '24PN', 'J3·7', "You're offline", 'What-if: the top shows what still works.')
m.gap('g_remove', 4080, Y3, **P.g('N2·6'))

m.e([m.c('d_kind', 'b'), (1255, 1730)], na=True)
m.e([(1255, 1730), (1135, 1730), m.c('g_notlink', 't')], label='Not TikTok or IG', lp=(1135, 1700), lw=110)
m.e([(1255, 1730), (1375, 1730), m.c('g_dup', 't')], label='Sent before', lp=(1375, 1700), lw=80)
m.v('e63', 'g_stop', label='Stop reading', lp=(1885, 1690), lw=90)
m.h('t_type', 't_pick', label='Picks one', lw=70)
m.e([m.c('d_why', 'b'), (3235, 1730)], na=True)
m.e([(2755, 1730), (3715, 1730)], na=True)
for n in ('f_priv', 'f_gone', 'f_none', 'f_fail', 'f_off'):
    x = m.c(n, 't')[0]
    m.e([(x, 1730), m.c(n, 't')])
for n in ('f_priv', 'f_gone'):
    x = m.c(n, 'b')[0]
    m.e([m.c(n, 'b'), (x, 2340)], na=True)
m.e([m.c('f_none', 'b'), (3235, 2340), (2200, 2340), m.c('t_type', 'b')], label='Types a place', lp=(2690, 2340), lw=100)
m.e([(3235, 2340), (4180, 2340), m.c('g_remove', 'b')], label='Or removes the link', lp=(3700, 2340), lw=140)

# ---------------- Row 4 · sorting into boards (Jamie, Thu 24 Sep)
m.pill('s_start', 40, Y4, 240, 'Jamie opens Boards', 'Thu 24 Sep · 7:35 PM', 'start')
m.card('e71', 350, Y4, '1QM5', 'E7·1', 'Boards', '6 boards, and 6 places not in a board yet.', True)
m.card('e73', 650, Y4, '1QTS', 'E7·3', 'Not in a board yet', 'Grouped by the link each place came from.', True)
m.card('e74', 950, Y4, '1QXI', 'E7·4', 'Pick two', 'Tampines Round Market and Bedok 85 Market.', True)
m.dia('d_boards2', 1315, Y4, 'Any boards yet?', sys=True)
m.card('e75', 1480, Y4, '1R1J', 'E7·5', 'Pick a board', 'Good fits first. + New board at the top.', True)
m.dia('d_dest', 1835, Y4, 'Which board?')
m.card('e76', 2020, Y4, '1R5C', 'E7·6', 'Added, Undo', 'Back on Not in a board yet, 4 left.', True)
m.pill('x4', 2310, Y4, 240, 'Build a plan from a board', '→ 4 · Making a plan', 'exit', jamie=True)
m.pill('j_first', 1200, Y4 + 175, 230, 'No boards yet', '→ Your first board (A5·2)', 'jump')
m.card('e77', 2640, Y4, '1R8X', 'E7·7', 'New board', 'Starts with the 2 places picked.')
m.card('e78', 2940, Y4, '1RC4', 'E7·8', 'Name it', 'Keyboard up. Make board with 2 places.')
m.gap('g_made', 3240, Y4, **P.g('N2·7'))
m.card('d43b', 3540, Y4, '1MID', 'D4·3b', 'New board, from +', 'Name it, then pick from Not in a board yet.')
m.pill('x_plusb', 3810, Y4, 220, 'From any tab: + → Board', 'the + in the bar', 'entry')

m.h('s_start', 'e71', 'coral')
m.h('e71', 'e73', 'coral', 'Not in a board yet', lw=90)
m.h('e73', 'e74', 'coral', 'Picks two', lw=70)
m.h('e74', 'd_boards2', 'coral', 'Add 2 places', lw=80)
m.h('d_boards2', 'e75', 'coral', 'Yes')
m.h('e75', 'd_dest', 'coral')
m.h('d_dest', 'e76', 'coral', 'Late-night zi char', lw=100)
m.h('e76', 'x4', 'coral')
m.v('d_boards2', 'j_first', label='No', lp=(1315, 2800))
m.e([m.c('d_dest', 'b'), (1835, 3040), (2740, 3040), m.c('e77', 'b')], label='+ New board', lp=(2290, 3040), lw=90)
m.h('e77', 'e78', label='Names it', lw=70)
m.h('e78', 'g_made', label='Make board', lw=80)
m.e([m.c('d43b', 'l'), m.c('g_made', 'r')], label='Make board', lw=80)
m.e([m.c('x_plusb', 'l'), m.c('d43b', 'r')])
# into sorting from above, through the gutter
m.e([m.c('d_add', 'b'), (4035, 2420), (750, 2420), m.c('e73', 't')], dash=True, label='Later · the places wait in Not in a board yet', lp=(2400, 2420), lw=270)
m.e([m.c('d_boards', 'b'), (4305, 2445), (1580, 2445), m.c('e75', 't')], label='Yes', lp=(3000, 2445))
m.e([m.c('t_pick', 'b'), (2500, 2465), (1315, 2465), m.c('d_boards2', 't')], label='Add 1 place to a board', lp=(1900, 2465), lw=150)

# ---------------- Row 5 · coming back to links and boards
m.pill('e_links', 40, Y5, 240, 'Jamie opens Links', 'Thu 24 Sep · 6:42 PM', 'start')
m.card('e51', 350, Y5, '1P9T', 'E5·1', 'Links', 'Reading 1, saved 13. A list, or a grid of covers.', True)
m.card('e53', 650, Y5, '1PI0', 'E5·3', 'A link, opened', 'Zi char past midnight: tap a place to open it, the circle to pick it.', True)
m.card('e54', 950, Y5, '1PLZ', 'E5·4', 'The place page', 'Why Jamie saved it. Add to a plan, Add to board.', True)
m.dia('d_place', 1315, Y5, 'Board or plan?')
m.pill('x_plan5', 1480, Y5, 220, 'Add to a plan', '→ 4 · Making a plan', 'exit')
m.card('e55', 1800, Y5, '1PP3', 'E5·5', 'A stall with no name', 'The video never says its name. Is it one of these?', True)
m.dia('d_one', 2165, Y5, 'One of these?')
m.pill('j_one', 2330, Y5, 220, 'This is the one', '↩ back to the link', 'jump')
m.gap('g_none', 2600, Y5, **P.g('N2·8'))
m.card('e72', 2900, Y5, '1QQ5', 'E7·2', 'One board', 'Open now first, then closed. Share at the top.')
m.gap('g_share2', 3200, Y5, **P.g('N2·9'))
m.gap('g_edit', 3600, Y5, **P.g('N2·10'))

m.h('e_links', 'e51', 'coral')
m.h('e51', 'e53', 'coral', 'Opens a link', lw=80)
m.h('e53', 'e54', 'coral', 'Taps a place', lw=80)
m.h('e54', 'd_place')
m.h('d_place', 'x_plan5', label='Add to a plan', lw=80)
m.e([m.c('d_place', 't'), (1315, 3140), (1440, 3140), (1440, 2465)], label='Add to board', lp=(1315, 3225), lw=90, na=True)
m.e([m.c('e53', 't'), (750, 3140), (1315, 3140)], label='Add 3 places to a board', lp=(1010, 3140), lw=150, na=True)
m.e([m.c('e53', 'b'), (750, 3740), (1900, 3740), m.c('e55', 'b')], 'coral', label='A stall with no name', lp=(1300, 3740), lw=140)
m.h('e55', 'd_one', 'coral')
m.h('d_one', 'j_one', 'coral', 'This is the one', lw=80)
m.e([m.c('d_one', 'b'), (2165, 3760), (2700, 3760), m.c('g_none', 'b')], label='None', lp=(2430, 3760))
m.e([m.c('e71', 'b'), (450, 3060), (3000, 3060), m.c('e72', 't')], label='Taps a board', lp=(2500, 3060), lw=90)
m.h('e72', 'g_share2', label='Share', lw=50)
m.e([m.c('e72', 'b'), (3000, 3760), (3700, 3760), m.c('g_edit', 'b')], label='Edit', lp=(3350, 3760))

m.render(P.out('j2'), W,
         'Journey 2 · Collecting', 'From a link to places to a board · Mon 28 Sep 2026',
         "Every way a video becomes places in a board. Jamie's first link runs along the top in coral; rows 4 and 5 follow Jamie on Thu 24 Sep. Grey paths are every other way through. Dashed cards are screens we still need to design.",
         [(1, "JAMIE'S FIRST LINK", 'Thu 2 Jul, 8:43 to 8:48 PM', True), (2, 'OTHER WAYS IN, AND WHILE ARGO READS', '', False),
          (3, "WHEN ARGO CAN'T READ IT", '', False), (4, 'SORTING INTO BOARDS', 'Jamie, Thu 24 Sep, 7:35 PM', True),
          (5, 'COMING BACK TO LINKS AND BOARDS', 'Jamie, Thu 24 Sep, 6:42 PM', True)],
         (3900, 3180, 1460, 'OPEN QUESTIONS', 'Answer these before the dashed cards get designed', [
             (1, 'Does a link that is reading take over the top? Chapter D says no, J3 shows yes. Rows 2 and 3 use J3 as a what-if.', True),
             (2, 'Paste: iOS asks "Allow Paste" every time unless Argo uses the system Paste button. Check with the developers.', True),
             (3, 'After Make board on a second board: land on the new board, or back where Jamie was?', True),
             (4, 'Stop reading: keep the places found so far, or drop them all?', True),
             (5, 'Remove this link: do its places leave their boards too?', True),
             (6, 'Is sharing a board (a view-only link) in the MVP?', True)]))
