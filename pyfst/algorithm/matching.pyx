from pyfst.fst import StdVectorFst
from pyfst.algorithm.util import make_fsa
from pytrie import Trie

def _direct(V):
    for sym in V:
        yield sym, tuple([sym])

def _masked(V):
    for sym, labels in V.iteritems():
        yield sym, labels

def substring_matcher(V, N, alpha, fst = StdVectorFst, sort = True):
    '''
    Builds the deterministic FSA (DFA) that reweights a substring (represented by a mask).
    @type V: dict (if N is a mask) or other set-like iterable (if N is directly specified in terms of the vocabulary)
    @param N: substring (sequence of "words")
    @type N: sequence
    @param alpha: weight
    @param fst: Fst constructor
    @return: label-sorted DFA

    '''
    assert len(N) > 1, 'At least a bigram is necessary'
    
    mapper = _masked if isinstance(V, dict) else _direct
    last = len(N)

    # initialize the FST
    f = make_fsa(states = last + 1, initial = 0, final = [0 , last], fst = fst)
    one = float(f.semiring()(True))

    weight = lambda destination: alpha if destination == last else one

    # trie that stores the reversed prefixes
    prefixes = Trie()
    for i in xrange(len(N)):
        prefixes[reversed(N[:i + 1])] = i + 1

    seen = set()

    for i in xrange(len(N)):
        for sym, labels in mapper(V):
            if sym == N[i]:
                w = weight(i + 1)
                [f.add_arc(i, i + 1, label, label, w) for label in labels]
            elif sym in seen:
                # symbols in seen loopback to j = (the state that remembers the longest suffix of the currently accepted string) or 0 if j does not exist
                key = tuple(reversed(N[:i] + tuple([sym])))
                _, sid = prefixes.longest_prefix_item(key, (None, 0))
                w = weight(sid)
                [f.add_arc(i, sid, label, label, w) for label in labels]
            else:
                # symbols other than N[i] and seen go back to 0
                [f.add_arc(i, 0, label, label, one) for label in labels]
        seen.add(N[i])
    
    # last state
    for sym, labels in mapper(V):
        if sym in seen:
            key = tuple(reversed(N + tuple([sym])))
            _, sid = prefixes.longest_prefix_item(key, (None, 0))
            w = weight(sid)
            [f.add_arc(last, sid, label, label, w) for label in labels]
        else:
            [f.add_arc(last, 0, label, label, one) for label in labels]

    if sort: f.arc_sort_input()
    return f

def trie_matcher(V, N, fst = StdVectorFst, sort = True):
    '''
    Builds the deterministic FSA (DFA) that reweights a substring.
    A substring maybe represented directly with the symbols of the vocabulary (in which case the vocabulary is a set of symbols),
    or indirectly by a mask, in which case the vocabulary is a dictionary that maps intermediate symbols to the terminal ones.
    Example: 
        N = [1,2,3]
        V = {1:[5,6], 2:[1,2], 3:[3,9], 4:[4,7,8]}

    @param V: vocabulary
    @type: dict or set
    @param N: substrings represented in a Trie which already contains the weights
    @return: label-sorted DFA

    '''

    one = float(fst.semiring()(True))

    seen = set()
    last = 0 # reserves 0 to the empty prefix
    P = Trie({tuple():last})
    stateinfo = [[one, True]] # pairs: weight, is_final

    # Enumerate reversed prefixes
    for ngram, w in N.iteritems():
        [seen.add(sym) for sym in ngram]
        head = N.longest_prefix(ngram[:-1], []) # finds whether this ngram is prefixed by another that is not itself (head)
        for i in xrange(len(head), len(ngram) - 1):  # enumerates all but the longest prefix of ngram that extend its head (the longest prefix is the ngram itself)
            rprefix = tuple(reversed(ngram[:i + 1])) # reverses the prefix
            last += 1
            P[rprefix] = last
            stateinfo.append([one, False])
        # includes the reversed ngram in the trie
        last += 1
        P[tuple(reversed(ngram))] = last
        stateinfo.append([w, True])

    # "percolating" weights: if we sort the reversed prefixes "alphabetically" then, we simply update each weight by summing the weight of its longest prefix
    # that is not itself and it is in the trie
    for rprefix, sid in sorted(P.iteritems(), key = lambda pair: pair[0]):
        head, state = P.longest_prefix_item(rprefix[:-1])
        stateinfo[sid][0] += stateinfo[state][0] # accumulate weights
        stateinfo[sid][1] |= stateinfo[state][1] # update 'is_final' property
    
    f = make_fsa(states = last + 1, initial = 0, final = (sid for sid, props in enumerate(stateinfo) if props[1]), fst = fst)

    # Transitions at each state
    # I am going to duplicate code, because it turned out to be 10-15% faster than using the mappers 
    if not isinstance(V, dict):
        unseen = frozenset(sym for sym in V).difference(seen)
        for rpfrom, sfrom in P.iteritems(): # rpfrom - departure reversed prefix 
            [f.add_arc(sfrom, 0, sym, sym, stateinfo[0][0]) for sym in unseen]
            for sym in seen:
                current = tuple([sym]) + rpfrom
                rpto, sto = P.longest_prefix_item(current)
                f.add_arc(sfrom, sto, sym, sym, stateinfo[sto][0])
    else:
        unseen = frozenset(sym for sym in V.iterkeys()).difference(seen)
        for rpfrom, sfrom in P.iteritems(): # rpfrom - departure reversed prefix 
            [[f.add_arc(sfrom, 0, label, label, stateinfo[0][0]) for label in V[sym]] for sym in unseen]
            for sym in seen:
                current = tuple([sym]) + rpfrom
                rpto, sto = P.longest_prefix_item(current)
                [f.add_arc(sfrom, sto, label, label, stateinfo[sto][0]) for label in V[sym]]

    if sort: f.arc_sort_input()
    return f

def path_matcher(V, P, fst = StdVectorFst, sort = True):
    '''
    Builds the deterministic FSA (DFA) that detects a set of paths.
    A path maybe represented directly with the symbols of the vocabulary (in which case the vocabulary is a set of symbols),
    or indirectly by a mask, in which case the vocabulary is a dictionary that maps intermediate symbols to the terminal ones.
    Example: 
        N = [1,2,3]
        V = {1:[5,6], 2:[1,2], 3:[3,9], 4:[4,7,8]}

    @param V: vocabulary
    @type: dict or set
    @param P: paths represented in a Trie (weights will be disregarded)
    @return: label-sorted DFA

    '''

    one = float(fst.semiring()(True))
    sto = 0
    prefixes = Trie({tuple():sto})
    arcs = []
    finals = set()
    for path in sorted(P.iterkeys()):
        head, sfrom = prefixes.longest_prefix_item(path[:-1])
        for i in xrange(len(head), len(path)):
            sto += 1
            prefixes[tuple(path[:i + 1])] = sto
            arcs.append([sfrom, sto, path[i]])
            sfrom = sto
        finals.add(sto)

    prefixes.clear()
    
    f = make_fsa(states = sto + 1, initial = 0, final = finals, fst = fst)

    if isinstance(V, dict):
        [[f.add_arc(sfrom, sto, sym, sym, one) for sym in V[label]] for sfrom, sto, label in arcs]
    else:
        [f.add_arc(sfrom, sto, sym, sym, one) for sfrom, sto, sym in arcs]

    if sort: f.arc_sort_input()
    return f
