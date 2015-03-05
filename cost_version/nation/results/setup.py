from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "cython functions for mcmc",
    ext_modules = cythonize('cyfuncs.pyx'), # accepts a glob pattern
)
