from _uf import P
from uf.states import StateMap

S = StateMap(P, 'The banner', 'Highest priority that applies wins.')
S.state('offline', 'Offline', 1, 'No signal', 'Signal returns', [('card', 'S1-0', 'A·1', 'Small')], note='Shows saved data.')
S.state('failed', 'Sign-in failed', 2, 'Sign-in fails', 'Try again', [('gap', 'N1·1', 'Small')], gives_way_to=['offline'], question='Q1·1')
if __name__ == '__main__':
    S.render('Fixture · the banner', 'fixture', 'States for tests.', 'states')
