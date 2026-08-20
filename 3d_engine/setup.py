from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
import sys

extra_compile_args = []
extra_link_args = []

if sys.platform == 'win32':
    # MSVC: use /O2 (closest to -O3)
    extra_compile_args = ['/O2']
else:
    # gcc/clang
    extra_compile_args = ['-O3', '-march=native']

ext_modules = [
    Pybind11Extension(
        name="_engine3d",
        sources=[
            'binding.cpp',
            'engine.cpp',
            'coordinate_transformation.cpp',
            'shading.cpp',
            'project_and_rasterizer.cpp',
        ],
        include_dirs=[pybind11.get_include(), '.' ],
        cxx_std=17,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="engine",
    version="0.1",
    description="CPU 3D engine Python bindings",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
