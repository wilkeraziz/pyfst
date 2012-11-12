from distutils.core import setup
from distutils.extension import Extension
import sys

suffix = '.cpp'
cmdcls = {}
try:
    sys.argv.remove('--cython')
    from Cython.Distutils import build_ext
    suffix = '.pyx'
    cmdcls['build_ext'] = build_ext
except ValueError:
    print 'Skipping cythoning'
except ImportError:
    print 'You do not seem to have Cython installed'


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
    cmdclass = cmdcls,
    name = 'pyfst',
    ext_modules= extensions,
    packages = ['pyfst'],
    package_dir = {'':'.'},

)
