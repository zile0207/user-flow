from _uf import P
from uf.promote import PromotedChapter

C = PromotedChapter(P, 1)
C.add('N1·4')
if __name__ == '__main__':
    C.render('Mon 1 Jan')
