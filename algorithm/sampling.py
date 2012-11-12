from numpy.random import uniform
from collections import Counter, defaultdict, deque
from fst import StdVectorFst, LogVectorFst
from bisect import bisect_left

from time import time
from random import random, randint
from util import network_fsa

class Path(tuple):
    """
    A weighted tuple that represents a path (convenient to use with dictionaries)
    """
    def __new__(cls, path, weights):
        new = super(Path, cls).__new__(cls, path)
        new._weights = tuple(weights)
        return new

    @property
    def weights(self):
        return self._weights

def sample(fst, totals, key = lambda sid, arc: arc.ilabel):
    """
    Samples a single path from an FST.
    @param fst: a connected FST (see fst.Fst.connect).
    @type fst: fst.Fst
    @param totals: total weight vector, that is, the total weight at each state (see fst.LogVectorFst.shortest_distance).
    @param key: the key of the transition.
    @type key: function, receives the state id and the Arc and returns a key representation of the transition.
    @return: a Path (i.e. a weighted tuple of transitions).
    """
    sid = fst.start
    path = []
    weights = []
    semiring = fst.semiring()
    while not fst[sid].final:
        th = semiring.from_real(uniform()) * totals[sid]
        acc = semiring(False)
        for arc in fst[sid]:
            acc += arc.weight * totals[arc.nextstate]
            if acc > th: break
        path.append(key(sid, arc))
        weights.append(float(arc.weight))
        sid = arc.nextstate
    return Path(path, weights)

def samples(fst, totals, n = 100, key = lambda sid, arc: arc.ilabel):
    """
    Samples multipe paths from an FST: this procedure simply wraps multiple class to C{sample}.

    @param fst: a connected FST (see fst.Fst.connect).
    @type fst: fst.Fst
    @param totals: total weight vector, that is, the total weight at each state.
    @param n: number of samples.
    @param key: the key of the transition.
    @type key: function, receives the state id and the Arc and returns a key representation of the transition.
    @return: a Counter of Path objects.
    """
    selection = Counter()
    for i in xrange(n):
        path = sample(fst, totals, key)
        selection[path] += 1
    return selection

class Prefix(object):
    """
    A prefix is a structure to organize incomplete sample paths
    """
    def __init__(self, last, n, path = []):
        self.path = path
        self.last = last
        self.n = n

def sample_transitions(fst, n, sfrom, totals):
    """
    Samples transitions leaving a single stae.
    @param fst: connected FST
    @type: fst.Fst
    @param n: number of samples
    @type n: int
    @param sfrom: state from which outgoing transitions should be sampled.
    @type sfrom: int
    @param totals: total future cost at each state (see percolate)
    @type totals: list of floats
    @return: a list of transitions, each transition being a tuple (sfrom, arc, #samples)
    """
    semiring = fst.semiring()
    total = totals[sfrom]
    ths = sorted(semiring.from_real(uniform()) * total for _ in xrange(n)) # sample n thresholds and sort them
    transitions = []
    low = 0
    acc = semiring(False)
    for arc in fst[sfrom]:
        acc += arc.weight * totals[arc.nextstate] # accumulate the weight of the path (arc's cost x future cost)
        # look for the insertion point of acc in ths: it has the property that all(val >= acc for val in ths[ipoint:])
        ipoint = bisect_left(ths, acc, low)
        if ipoint > low:
            # acc < th for `ipoint - low` values of th
            transitions.append((sfrom, arc, ipoint - low))
        low = ipoint # next time we ignore ths' head
        if low == n:
            break
    return transitions

def deque_samples(fst, totals, n = 100, key = lambda sid, arc: arc.ilabel):
    """
    Samples multipe paths from an FST: this procedure uses a deque to expand prefixes, sampling multiple times in one go over the deque.
    It may be more efficient than C{samples} when many paths are expected to share few prefixes.

    @param fst: a connected FST (see fst.Fst.connect).
    @type fst: fst.Fst
    @param totals: total weight vector, that is, the total weight at each state.
    @param n: number of samples.
    @param key: the key of the transition.
    @type key: function, receives the state id and the Arc and returns a key representation of the transition.
    @return: a Counter of Path objects.
    
    """
    samples = Counter()
    # we start with an empty prefix, for which we start sampling n samples from the initial state of the fsa
    Q = deque([Prefix(fst.start, n)])
    while Q: # while the are prefixes
        prefix = Q.popleft() # get the first
        if fst[prefix.last].final: # if we have reached a final state
            # we stop expanding that prefix (which is now a complete path) and keep it (n times)
            samples[Path([key(sid, arc) for sid, arc in prefix.path], [float(arc.weight) for _, arc in prefix.path])] = prefix.n
        else:
            # otherwise we get sample prefix.n transitions
            transitions = sample_transitions(fst, prefix.n, prefix.last, totals)
            # and expand the prefix with the sampled transitions
            for sfrom, arc, times in transitions:
                Q.append(Prefix(arc.nextstate, times, prefix.path + [(sfrom, arc)]))
    return samples

def main():
    """
    Test
    """
    A = defaultdict(lambda : defaultdict(int))
    A[0][1] = [1, 2]
    A[0][2] = [2, 1]
    A[1][3] = [3, 2]
    A[1][4] = [4, 4]
    A[2][3] = [5, 6]
    A[2][4] = [6, 2]
    A[3][5] = [7, 1]
    A[4][5] = [8, 2]
    
    def custom(sfrom, sto):
        label = sto
        w = random()
        if sto % 101 != 1:
            w += randint(5,15)
        return label, w

    t0 = time()
    small = network_fsa(2, 2, arc = lambda sfrom, sto: A[sfrom][sto])
    t1 = time()
    print 'Small: states %d arcs %d time %f' % (len(small), small.num_arcs(), t1-t0)
    
    t0 = time()
    big = network_fsa(20, 400, arc = custom)
    t1 = time()
    print 'Big: states %d arcs %d time %f' % (len(big), big.num_arcs(), t1-t0)

    N = 1000
    printing = 10
    for f in [small, big]:
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
        for path, n in dist.most_common(printing):
            print ' ',n, path
        print '', N, 'samples', t1-t0

        print 'deque_samples'
        t0 = time()
        dist = deque_samples(f, totals, N)
        t1 = time()
        for path, n in dist.most_common(printing):
            print ' ',n, path
        print '', N, 'samples', t1-t0

if __name__ == '__main__':
    main()
