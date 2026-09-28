from _uf import P
from uf.explore import render
from ui_kit import phone, title

SPEC = {
    'id': 'N1·1', 'title': 'Sign-in failed', 'source': 'from Journey 1, row 2',
    'journey': {'name': 'Journey 1', 'artboard': 'TEST', 'card_xy': (0, 0)},
    'status': {'state': 'confirmed', 'chosen': 'A', 'round': 1, 'date': 'Mon 1 Jan'},
    'brief': {'needs': 'Say what went wrong.', 'musts': ['Says why', 'Offers Try again'],
              'where': [('outside', 'OUTSIDE', 'Google'), ('this', 'N1·1 · THIS', 'Sign-in failed'), ('outside', 'NEXT', 'Home')]},
    'refs_source': 'mobbin',
    'refs': [{'img': P.refs_dir + '/r1.png', 'name': 'App', 'take': 'A calm error.', 'url': 'https://example.com'}],
    'rounds': [{'date': 'Mon 1 Jan', 'ask': None, 'directions': [
        {'letter': 'A', 'title': 'Inline', 'idea': 'Error on the same screen.', 'good': 'fast.', 'costs': 'small.', 'inspired': 'App.',
         'screens': [{'label': 'Error', 'html': phone('A·1 · Error', title("Couldn't sign you in"))}]},
        {'letter': 'B', 'title': 'Sheet', 'idea': 'A sheet explains.', 'good': 'clear.', 'costs': 'slower.', 'inspired': 'App.',
         'screens': [{'label': 'Error', 'html': phone('B·1 · Error', title('Something went wrong'))}]},
    ]}],
}
if __name__ == '__main__':
    render(P, 'explore', SPEC)
