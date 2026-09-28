"""Journey 1 · Getting in. Spec for the live board '1 · Getting in · journey map' (includes the 28 Sep decisions)."""
from _uf import P
from uf.jmap import Map, row_y

W = 5440
Y1, Y2, Y3, Y4 = row_y(1), row_y(2), row_y(3), row_y(4)
m = Map(1, P.img_dir)

# ---------------- Row 1 · Jamie's path
m.pill('start', 40, Y1, 180, 'Jamie opens Argo', 'Thu 2 Jul · 8:30 PM', 'start')
m.dia('d0', 355, Y1, 'Signed in on this phone?', sys=True)
m.card('b1', 520, Y1, '1CH7', 'A1·1', 'Discover', 'Three slides. Skip on any of them.', True)
m.card('b2', 820, Y1, '1CI5', 'A1·2', 'Save', 'Second slide.', True)
m.card('b3', 1120, Y1, '1CJ3', 'A1·3', 'Plan', 'Last slide: Get started.', True)
m.card('b4', 1420, Y1, '1CK2', 'A1·4', 'Ready when you are', 'New or returning, both go to one sign-in.', True)
m.card('b5', 1720, Y1, '1CKY', 'A1·5', 'Sign in', 'Email, Google or Apple. Back returns to 4.', True)
m.dia('d3', 2065, Y1, 'Which way in?')
m.card('b6', 2230, Y1, '1CME', 'A1·6', 'Google account', "Google's sheet over the app.", True)
m.card('b7', 2530, Y1, '1COX', 'A1·7', 'Signing in', 'A second or two.', True)
m.dia('d4', 2875, Y1, 'Signed in?', sys=True)
m.dia('d5', 3135, Y1, 'New account?', sys=True)
m.card('b8', 3300, Y1, '1CP8', 'A1·8', 'Pick interests', 'Jamie picks 5: Hawker, Late nights, Live music, Nature, Markets.', True)
m.dia('d6', 3645, Y1, 'Pick or skip?')
m.card('b9', 3830, Y1, '1CR1', 'A1·9', 'Location and alerts', 'One screen asks for both.', True)
m.dia('d7', 4175, Y1, 'Allow both or not now?')
m.card('b10', 4360, Y1, '1CSB', 'A1·10', 'Building the feed', 'Argo puts Explore together.', True)
m.dia('d8', 4705, Y1, 'Feed ready?', sys=True)
m.card('do1', 4850, Y1, '1CSI', 'A1·11', 'First open', 'The top asks for a link. Explore uses the 5 interests.', True)
m.pill('x1', 5140, Y1 - 100, 250, 'Build one now', '→ 4 · Making a plan (A2)', 'exit', jamie=True)
m.pill('x2', 5140, Y1, 250, 'Tap around the tabs', '→ 7 · Always there (A3)', 'exit', jamie=True)
m.pill('x3', 5140, Y1 + 100, 250, 'Paste the first link', '→ 2 · Collecting (A4)', 'exit', jamie=True)

for a, b, lab, lw in [('start', 'd0', None, None), ('d0', 'b1', 'No', None), ('b1', 'b2', 'Next', None), ('b2', 'b3', 'Next', None),
                      ('b3', 'b4', 'Get started', 90), ('b4', 'b5', 'Create an account', 90), ('b5', 'd3', None, None), ('d3', 'b6', 'Google', None),
                      ('b6', 'b7', "Jamie's account", 90), ('b7', 'd4', None, None), ('d4', 'd5', 'Yes', None), ('d5', 'b8', 'Yes', None),
                      ('b8', 'd6', None, None), ('d6', 'b9', 'Continue', 100), ('b9', 'd7', None, None), ('d7', 'b10', 'Not now', 100),
                      ('b10', 'd8', None, None), ('d8', 'do1', 'Yes', None)]:
    m.h(a, b, 'coral', lab, lw=lw)
r = m.c('do1', 'r')
for xi in ('x1', 'x2', 'x3'):
    tt = m.c(xi, 'l'); m.e([r, (r[0] + 45, r[1]), (r[0] + 45, tt[1]), tt], 'coral')
L = 345
m.e([(620, 380), (620, L), (1520, L), (1520, 380)], label='Skip, on any slide', lp=(1010, L))
m.e([(920, 380), (920, L)], na=True); m.e([(1220, 380), (1220, L)], na=True)
m.e([(2330, 380), (2330, L), (1820, L), (1820, 380)], label='Cancel', lp=(2075, L))

# ---------------- Row 2 · other ways through onboarding
m.gap('g2', 1700, Y2, **P.g('N1·1'))
m.gap('g3', 1965, Y2, **P.g('N1·2'))
m.gap('g4', 2775, Y2, **P.g('N1·3'))
m.gap('g5', 3035, Y2, **P.g('N1·4'))
m.pill('j6', 3530, Y1 + 150, 230, 'Skipped', 'asked once more later · row 3', 'jump')
m.gap('g6', 4075, Y2, **P.g('N1·5'))
m.gap('g7', 4360, Y2, **P.g('N1·6'))
m.gap('g8', 4605, Y2, **P.g('N1·7'))
m.gap('g13', 4850, Y2, **P.g('N1·8'))
m.pill('j4', 2745, Y2 + 375, 260, 'Try again', '↩ back to 5 · Sign in', 'jump')
m.pill('j5', 3045, Y2 + 375, 180, 'Explore', '→ 7 · Always there', 'exit')
m.pill('j8', 4615, Y2 + 375, 180, 'Try again', '↩ back to 10', 'jump')

b3 = m.c('d3', 'b'); F = 1010
m.e([b3, (b3[0], m.c('g3', 't')[1])], label='Email', lp=(b3[0], 900))
m.e([(b3[0], F), (m.c('g2', 't')[0], F), m.c('g2', 't')], label='Apple', lp=(1880, F))
M = 1610; bx = m.c('b7', 'b')[0]
m.e([m.c('g2', 'b'), (m.c('g2', 'b')[0], M), (bx, M), (bx, m.c('b7', 'b')[1])], label='Signed in', lp=(2400, M))
m.e([m.c('g3', 'b'), (m.c('g3', 'b')[0], M)], na=True)
m.v('d4', 'g4', label='No', lp=(2875, 780)); m.v('g4', 'j4')
m.v('d5', 'g5', label='No, returning', lp=(3135, 780), lw=100); m.v('g5', 'j5')
m.v('d6', 'j6', dash=True, label='Skip, or none picked', lp=(3645, 690), lw=140)
m.v('d7', 'g6', label='Allow both', lp=(4175, 850), lw=90)
m.h('g6', 'g7', label='Either answer', lw=80)
m.e([m.c('g7', 't'), (m.c('g7', 't')[0], m.c('b10', 'b')[1])])
m.v('d8', 'g8', label='No', lp=(4705, 850)); m.v('g8', 'j8')
m.v('do1', 'g13', dash=True, label='If 8 was skipped', lp=(4970, 965), lw=120)

# ---------------- Row 3 · on a later open
m.dia('d0b', 355, Y3, 'Finished onboarding?', sys=True)
m.pill('e9', 470, Y3 - 170, 250, 'From 8 · Skip or none', 'nothing picked on 8', 'entry')
m.dia('d9', 595, Y3, 'No interests, not asked yet?', sys=True)
m.card('do2', 760, Y3, '1FFZ', 'A7·1', 'Tell Argo what you like', 'In the top, once, on a later open. MVP version drops Take the quiz.')
m.dia('d10', 1105, Y3, 'What does the user do?')
m.gap('g9', 1270, Y3, **P.g('N1·9'))
m.pill('x9', 1560, Y3, 200, 'Explore', '→ 7 · Always there', 'exit')
m.pill('e11', 1900, Y3, 230, 'From 9 · Not now', 'location was skipped', 'entry')
m.card('do3', 2200, Y3, '1F5T', 'A6·1', 'New near you asks', 'Jamie scrolls Explore. Location is still off.')
m.card('do4', 2500, Y3, '1FA8', 'A6·2', 'The phone asks', "iOS alert with Argo's reason in it.")
m.dia('d11', 2845, Y3, 'Allow?')
m.gap('g11', 3010, Y3, **P.g('N1·10'))
m.pill('x12', 3330, Y3, 330, 'From 9 · Not now (alerts)', 'asked while the first link reads · 2 · Collecting (A4·4)', 'entry')
m.e([m.c('d0', 'b'), m.c('d0b', 't')], label='Yes', lp=(355, 720))

# ---------------- Row 4 · edge cases of row 3
m.pill('j_restart', 235, Y4, 240, 'Restart onboarding', '↩ back to 1 · Discover, nothing kept', 'jump')
m.pill('x0', 495, Y4, 200, 'Explore', '→ 7 · Always there', 'exit')
m.gap('g10', 1005, Y4, **P.g('N1·11'))
m.pill('e12', 2440, Y4, 270, 'From onboarding', "Don't Allow on the location alert", 'entry')
m.gap('g12', 2745, Y4, **P.g('N1·12'))

m.h('d0b', 'd9', label='Yes')
m.v('d0b', 'j_restart', label='No', lp=(355, 2200))
m.v('e9', 'd9', dash=True)
m.h('d9', 'do2', label='Yes')
m.v('d9', 'x0', label='No', lp=(595, 2200))
m.h('do2', 'd10')
m.h('d10', 'g9', label='Save these', lw=90)
m.h('g9', 'x9')
m.v('d10', 'g10', dash=True, label='Take the quiz · after MVP', lp=(1105, 2200), lw=120)
tq = m.c('d10', 't'); tx = m.c('x9', 't')
m.e([tq, (tq[0], 1725), (tx[0], 1725), tx], label="Swipe it away · won't ask again", lp=(1380, 1725), lw=210)
m.h('e11', 'do3', dash=True)
m.h('do3', 'do4', label='Use my location', lw=90)
m.h('do4', 'd11')
m.h('d11', 'g11', label='Allow', lw=70)
m.v('d11', 'g12', label="Don't Allow", lp=(2845, 2200), lw=90)
m.h('e12', 'g12', dash=True)

if __name__ == '__main__':
    m.render(P.out('j1'), W,
             'Journey 1 · Getting in', 'From install to the first open, and what comes back later · Mon 28 Sep 2026',
             "Every way into Argo. Jamie's path runs along the top in coral, and every other way through branches off it and joins back. Dashed cards are screens we still need to design: each one says what it has to show.",
             [(1, "JAMIE'S PATH", 'Thu 2 Jul, 8:30 to 8:52 PM', True), (2, 'OTHER WAYS THROUGH ONBOARDING', '', False),
              (3, 'ON A LATER OPEN', 'what was skipped comes back once, where it is needed', False)],
             (3800, 2240, 1600, 'DECISIONS · MON 28 SEP', 'Amber is still open', [
                 (1, 'Interests: the 14 onboarding words for now. The Profile page will match them. Confirm with the developers.', True),
                 (2, 'Continue works with nothing picked. Plans stay generic, like Skip.', False),
                 (3, 'Email sign-in: password, or a code sent to the email? Pick one before N1·2 is designed.', True),
                 (4, 'The quiz comes after MVP. For MVP, A7·1 shows only Save these.', False),
                 (5, 'A returning account on a new phone skips onboarding but is asked for location and alerts.', False),
                 (6, 'Closed mid-onboarding: it starts again from 1.', False)]),
             dividers=(960, 1692))
