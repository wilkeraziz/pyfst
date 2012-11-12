from pyfst.fst import LogVectorFst
from pyfst.algorithm.util import network_fsa
from pyfst.algorithm.sampling import samples, deque_samples
from collections import defaultdict
from random import random, randint
from time import time

def small():
    A = defaultdict(lambda : defaultdict(int))
    A[0][1] = [1, 2]
    A[0][2] = [2, 1]
    A[1][3] = [3, 2]
    A[1][4] = [4, 4]
    A[2][3] = [5, 6]
    A[2][4] = [6, 2]
    A[3][5] = [7, 1]
    A[4][5] = [8, 2]
    
    t0 = time()
    f = network_fsa(2, 2, arc = lambda sfrom, sto: A[sfrom][sto])
    t1 = time()
    print 'Small: states %d arcs %d time %f' % (len(f), f.num_arcs(), t1-t0)
    return f

def big():
    def custom(sfrom, sto):
        label = sto
        w = random()
        if sto % 101 != 1:
            w += randint(5,15)
        return label, w

    t0 = time()
    f = network_fsa(20, 400, arc = custom)
    t1 = time()
    print 'Big: states %d arcs %d time %f' % (len(f), f.num_arcs(), t1-t0)
    return f

def test(f, N = 1000, top = 10):
    t0 = time()
    f = LogVectorFst(f)
    t1 = time()
    print 'Tropical -> Log', t1-t0

    t0 = time()
    totals = f.shortest_distance(True)
    t1 = time()
    print 'shortest distance', t1-t0

    print 'samples'
    t0 = time()
    dist = samples(f, totals, N)
    t1 = time()
    for path, n in dist.most_common(top):
        print ' ',n, path
    print '', N, 'samples', t1-t0

    print 'deque_samples'
    t0 = time()
    dist = deque_samples(f, totals, N)
    t1 = time()
    for path, n in dist.most_common(top):
        print ' ',n, path
    print '', N, 'samples', t1-t0

if __name__ == '__main__':
    test(small())
    test(big())
