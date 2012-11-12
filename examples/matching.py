from pyfst.algorithm.matching import substring_matcher, trie_matcher
from pyfst.algorithm.util import path_fsa, draw
from pytrie import Trie
from time import time



dfaSM1 = substring_matcher(range(1,4), [1,2,1,2], 10) 
draw(dfaSM1, 'matching-substring1')
print 'matching-substring1'

dfaSM2 = substring_matcher({'the':[1,2], 'black':[3,4], 'dog':[5,6], 'barked':[7,8]}, ['the', 'black', 'the'], 10) 
draw(dfaSM2, 'matching-substring2')
print 'mathching-substring2'

N1 = Trie()
N1[tuple([2,3])] = 1
N1[tuple([1,2,3])] = 2
N1[tuple([2,3,4])] = 3
N1[tuple([1,2,3,4])] = 4
N1[tuple([4,1])] = 5
N1[tuple([1,2])] = 0.5
V = range(1,200000)
t0 = time()
dfaTM1 = trie_matcher(V, N1)
t1 = time()
print 'trie matcher', t1-t0
p1 = [1,2,3,4,1,2,3,4]
draw(dfaTM1.intersect(path_fsa(p1)), 'matching-trie1')
