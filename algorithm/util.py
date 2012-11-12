import gv
from fst import StdVectorFst
from random import random

def draw(fst, stem, ext = 'png', isym = None, osym = None, ssym = None):
    """
    Draws an FST in one of the available formats (depends on gv).
    @param fst: FST.
    @type fst: pyfst.fst.Fst
    @param stem: path except for extension.
    @param ext: output type (defaults to png).
    """
    with open(stem + '.dot', 'wb') as D:
        D.write(fst.draw(isym, osym))
    
    dot = gv.read(stem + '.dot')
    gv.layout(dot, 'dot')
    gv.render(dot, ext, stem + '.' + ext)

def make_fsa(states = 0, initial = -1, final = [], arcs = [], sort = False, Fst = StdVectorFst):
    """
    Builds an FSA.
    @param states: number of states
    @param initial: initial state
    @param final: final states (int or iterable)
    @param arcs: list of transitions (each transition is a tuple: origin, destination, label, weight)
    @param sort: ilabel-sorts before returning
    @param Fst: type of Fst (defaults to fst.StdVectorFst)
    """
    f = Fst()
    [f.add_state() for _ in xrange(states)] 
    if initial >= 0:
        f.start = initial
    one = float(f.semiring()(True))
    if type(final) is int:
        f[final].final = one
    else:
        for sid in final:
            f[sid].final = one
    [f.add_arc(sfrom, sto, label, label, weight) for sfrom, sto, label, weight in arcs]
    if sort:
        f.arc_sort_input()
    return f


def path_fsa(path, weights = None, label = lambda transition: transition, Fst = StdVectorFst):
    """Makes an acceptor out of a path of transitions and scores.
    Each transition i is weighted as weights[i] (or ONE if not specified) and labelled as label(path[i]).
    @param path: sequence of transitions.
    @param weights: sequence of weights (defaults to a sequence of ONEs).
    @param label: a function that returns the label (int) of a transition.
    @param Fst: FST type (defaults to fst.StdVectorFst)
    @return: fst.Fst
    """
    N = len(path) + 1
    f = make_fsa(states=N, initial=0, final=N - 1, Fst = Fst)
    if weights is None:
        one = float(f.semiring()(True))
        w = lambda sid : one
    else:
        w = lambda sid: weights[sid]
    [f.add_arc(i, i + 1, label(arc), label(arc), w(i)) for i, arc in enumerate(path)]
    return f

def network_fsa(nLayer, sLayer, arc = lambda sfrom, sto: (sto, random()), Fst = StdVectorFst):
    """
    Makes an FSA that has n layers in between the initial and the final state.
    Each layer has m states and every state in layer i is connected to every state in layer i+1.

    @param nLayer: number of layers.
    @param sLayer: size of each layer.
    @param arc: function that receives origin and destination and returns a label and a weight.
    @param Fst: FST type (defaults to StdVectorFst).
    """
    f = make_fsa(states = nLayer * sLayer + 2, initial = 0, final = nLayer * sLayer + 1)
    
    for n in xrange(nLayer - 1):
        for i in xrange(sLayer):
            sfrom = n * sLayer + i + 1
            for j in xrange(sLayer):
                sto = (n + 1) * sLayer + j + 1
                l, w = arc(sfrom, sto)
                f.add_arc(sfrom, sto, l, l, w)

    for i in xrange(sLayer):
        l, w = arc(0, i + 1)
        f.add_arc(0, i + 1, l, l, w)
        sfrom = (nLayer - 1) * sLayer + i + 1
        sto = nLayer * sLayer + 1
        l, w = arc(sfrom, sto)
        f.add_arc(sfrom, sto, l, l, w)

    return f

def main():
    """
    Test
    """
    p = path_fsa([10, 20, 30])
    draw(p, 'examples/util.path')
    wp = path_fsa([(1,10), (2,20), (3,30)], weights = [0.5, 0.6, 0.7], label = lambda pair: pair[1])
    draw(wp, 'examples/util.wpath')

    wfsa = make_fsa(6, 0, 5, sort = True,
            arcs = [
                (0,1,1,1),
                (0,2,2,1),
                (1,3,3,2),
                (1,4,4,4),
                (2,3,3,2.5),
                (2,4,4,5),
                (3,5,5,1),
                (4,5,5,1)
                ])
    draw(wfsa, 'examples/util.wfsa')

    net = network_fsa(3,3)
    draw(net, 'examples/util.net')

if __name__ == '__main__':
    main()
