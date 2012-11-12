from numpy.random import uniform
from collections import Counter, deque
from pyfst.fst import StdVectorFst, LogVectorFst
from bisect import bisect_left

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
    return Counter(sample(fst, totals, key) for _ in xrange(n))

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
            [Q.append(Prefix(arc.nextstate, times, prefix.path + [(sfrom, arc)])) for sfrom, arc, times in transitions]
    return samples

