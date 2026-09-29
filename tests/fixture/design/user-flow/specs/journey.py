from _uf import P
from uf.jmap import Map, row_y

m = Map(1, P)
Y1, Y2 = row_y(1), row_y(2)
m.seq(Y1, 40, [
    ('pill', 'start', dict(w=180, text='Sam opens the app', sub='Mon', style='start'), 70),
    ('card', 's1', dict(node='S1-0', ref='A·1', title='Welcome', note='First screen.', jamie=True), 90),
    ('dia', 'd1', dict(text='Signed in?', sys=True), 90),
    ('card', 's2', dict(node='S2-0', ref='A·2', title='Home', note='Done.', jamie=True), 70),
])
m.gap('g1', m.under('d1', Y2), Y2, **P.g('N1·1'))
m.gap('g2', 900, Y2, **P.g('N1·2'))
m.gap('g3', 1160, Y2, **P.g('N1·3'))
m.h('start', 's1', 'coral')
m.h('s1', 'd1', 'coral', 'Continue', lw=80)
m.h('d1', 's2', 'coral', 'Yes')
m.v('d1', 'g1', label='No', lp=(m.c('d1', 'b')[0], 760))
m.e([m.c('g2', 'b'), (1000, 1640), (1260, 1640), m.c('g3', 'b')], dash=True, label='Later', lp=(1130, 1640))
if __name__ == '__main__':
    m.render(P, 'journey', 1600, 'Journey 1 · Test', 'fixture', 'A small journey for tests.',
             [(1, "SAM'S PATH", 'Mon', True), (2, 'OTHER WAYS', '', False)], P.panel('J1', 1300, 300, 400))
