from pyfst.algorithm.util import draw, path_fsa, make_fsa, network_fsa

p = path_fsa([10, 20, 30])
draw(p, 'util-path')
wp = path_fsa([(1,10), (2,20), (3,30)], weights = [0.5, 0.6, 0.7], label = lambda pair: pair[1])
draw(wp, 'util-wpath')

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
draw(wfsa, 'util-wfsa')

net = network_fsa(3,3)
draw(net, 'util-net')

