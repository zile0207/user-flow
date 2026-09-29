from _uf import P
from uf.master import MasterMap

M = MasterMap(P, columns=2)
M.area('Start', 'A · app/(auth)', [('card', 'S1-0', 'A·1', 'Welcome'), ('gap', 'N1·1'), ('gap', 'N1·2')], entries='first launch')
M.area('Home', 'B · app/(tabs)', [('card', 'S2-0', 'A·2', 'Home'), ('gap', 'N1·3')])
if __name__ == '__main__':
    M.render('Fixture · every screen', 'fixture', 'Master map for tests.')
