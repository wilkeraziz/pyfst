# pyfst

Python interface to [OpenFst](http://openfst.org)

## Installation

1. Install the latest version of OpenFst (1.3.2)

2. `pip install -e git+https://github.com/vchahun/pyfst.git#egg=pyfst`

3. Or you can do

        python setup.py build_ext -i [--mustache] [--cython]

    If you use the option `--mustache` the mustache templates will be used to generate `fst.pyx` and `cfst.pxd` (requires [mustache](http://mustache.github.com/)).

    If you use the option `--cython` the setup will compile pyx files into cpp files (requires [Cython 0.17.1](http://cython.org)).

## Usage

The [basic example](http://www.openfst.org/twiki/bin/view/FST/FstQuickTour#CreatingFsts) from the documentation translates to:

```python
from fst import StdVectorFst

t = StdVectorFst()

t.start = t.add_state()

t.add_arc(0, 1, 1, 1, 0.5)
t.add_arc(0, 1, 2, 2, 1.5)

t.add_state()
t.add_arc(1, 2, 3, 3, 2.5)

t.add_state()
t[2].final = 3.5

t.write('binary.fst')
```

A simplified FST class is available:
```python
from fst import SimpleFst

t = SimpleFst()

t.add_arc(0, 1, 'a', 'A', 0.5)
t.add_arc(0, 1, 'b', 'B', 1.5)
t.add_arc(1, 2, 'c', 'C', 2.5)

t[2].final = 3.5

t.shortest_path() # 2 -(a:A/0.5)-> 1 -(c:C/2.5)-> 0/3.5 
```

## Examples

In `examples` you will find a bunch of test cases, e.g. `edit.py`, `sampling.py`, `matching.py`, etc.

## IPython notebook

The pyfst API is [IPython notebook](http://ipython.org/ipython-doc/dev/interactive/htmlnotebook.html)-friendly: the transducers objects are [automatically drawn](http://nbviewer.ipython.org/3835477/) using [Graphviz](http://www.graphviz.org).
