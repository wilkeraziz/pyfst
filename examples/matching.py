from pyfst.algorithm.matching import substring_matcher, trie_matcher
from pyfst.algorithm.util import path_fsa, draw
from pytrie import Trie
from time import time
import sys

if len(sys.argv) < 5:
    print >> sys.stderr, 'Usage: python %s substring|trie outstem vocab [pattern/weight]+ < queries' % sys.argv[0]
    print >> sys.stderr, 'Examples: echo "4 5 1 2 3 6" | python %s substring matching-substring 1-10 1,2,3/2' % sys.argv[0]
    print >> sys.stderr, 'Examples: echo "5 3 1 2 3 4" | python %s trie matching-trie 1-10 1,2,3/2 1,2/1 3,1,2,3/5' % sys.argv[0]
    sys.exit(0)

alg = sys.argv[1]
ostem = sys.argv[2]
lower, upper = sys.argv[3].split('-')
lower, upper = int(lower), int(upper)
patterns = sys.argv[4:]
V = range(lower, upper + 1)

if alg == "substring":
    if len(patterns) != 1:
        print sys.stderr, "I'm using only the first pattern"
    pattern, weight = patterns[0].split('/')
    print 'pattern: %s (%s)' % (pattern, weight)
    pattern = [int(x) for x in pattern.split(',')]
    weight = float(weight)
    dfa = substring_matcher(V, pattern, weight)
    draw(dfa, ostem)
    try:
        while True:
            query = [int(x) for x in raw_input().split()]
            f = path_fsa(query)
            f = dfa.intersect(f)
            for path in f.paths():
                arcs = [(arc.ilabel, float(arc.weight)) for arc in path]
                print '%s: %f' % (' '.join(['%d:%s' % (l, str(w)) for l, w in arcs]), sum(w for l, w in arcs))
    except EOFError:
        sys.exit(0)
        
elif alg == "trie":
    trie = Trie()
    for pattern in patterns:
        pattern, weight = pattern.split('/')
        print '+pattern: %s (%s)' % (pattern, weight)
        pattern = tuple(int(x) for x in pattern.split(','))
        weight = float(weight)
        trie[pattern] = weight
    dfa = trie_matcher(V, trie)
    draw(dfa, ostem)
    try:
        while True:
            query = [int(x) for x in raw_input().split()]
            f = path_fsa(query)
            f = dfa.intersect(f)
            for path in f.paths():
                arcs = [(arc.ilabel, float(arc.weight)) for arc in path]
                print '%s: %f' % (' '.join(['%d:%s' % (l, str(w)) for l, w in arcs]), sum(w for l, w in arcs))
    except EOFError:
        sys.exit(0)
else:
    print >> sys.stderr, "Unknown algorithm", alg

