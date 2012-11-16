from distutils.core import setup
from distutils.extension import Extension
import sys
import os

ymls = ['pyfst/types.yml']
tpls = ['pyfst/cfst.pxd.tpl', 'pyfst/fst.pyx.tpl']

# treats the switch --mustache
try:
    sys.argv.remove('--mustache')
    if os.system('mustache -v') != 0:
        raise OSError, "You don't seem to have `mustache` installed"
    types = ' '.join(ymls)
    for tpl in tpls:
        src = tpl[:-4] # removes .tpl
        cmd = 'cat %s %s | mustache > %s' % (types, tpl, src)
        if os.system(cmd) != 0:
            raise OSError, "Problem running: %s" % cmd
        else: 
            print cmd, '[success]'
except ValueError:
    print 'Skipping mustaching'

# treats the switch --cython
cythoning = False
try:
    sys.argv.remove('--cython')
    from Cython.Distutils import build_ext
    cythoning = True
except ValueError:
    print 'Skipping cythoning'
except ImportError:
    print 'You do not seem to have Cython installed'

suffix = '.pyx' if cythoning else '.cpp'
extensions = [
            Extension(name='pyfst.fst',
                sources=['pyfst/fst' + suffix],
                include_dirs=['.'],
                libraries=['z', 'fst'],
                language='c++',
                extra_compile_args=['-O2']
                ),
            Extension(name='pyfst.algorithm.util',
                sources=['pyfst/algorithm/util' + suffix],
                include_dirs=['.'],
                language='c++',
                extra_compile_args=['-O2']
                ),
            Extension(name='pyfst.algorithm.sampling',
                sources=['pyfst/algorithm/sampling' + suffix],
                include_dirs=['.'],
                language='c++',
                extra_compile_args=['-O2']
                ),
            Extension(name='pyfst.algorithm.matching',
                sources=['pyfst/algorithm/matching' + suffix],
                include_dirs=['.'],
                language='c++',
                extra_compile_args=['-O2']
                ),
            ]

setup(
    cmdclass = {'build_ext':build_ext} if cythoning else {},
    name = 'pyfst',
    ext_modules= extensions,
    packages = ['pyfst'],
    package_dir = {'':'.'},

)
