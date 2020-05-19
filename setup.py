#!/usr/bin/python3

#from __future__ import print_function
from setuptools import setup, Extension
import sys
import os
import psutil

# monkey-patch for parallel compilation
def parallelCCompile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    
    N = psutil.cpu_count(logical=False) # number of parallel compilations
    import multiprocessing.pool
    def _single_compile(obj):
        try: src, ext = build[obj]
        except KeyError: return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    # convert to list, imap is evaluated on-demand
    list(multiprocessing.pool.ThreadPool(N).imap(_single_compile,objects))
    return objects

#import distutils.ccompiler
#distutils.ccompiler.CCompiler.compile=parallelCCompile


''' Note:

to build Boost.Python on Windows with mingw

bjam target-os=windows/python=3.4 toolset=gcc variant=debug,release link=static,shared threading=multi runtime-link=shared cxxflags="-include cmath "


also insert this on top of boost/python.hpp :

#include <cmath>   //fix  cmath:1096:11: error: '::hypot' has not been declared

'''


def getExtensions():
    platform = sys.platform

    extensionsList = []
    sources = ['src/Genome.cpp',
               'src/Innovation.cpp',
               'src/NeuralNetwork.cpp',
               'src/Parameters.cpp',
               'src/PhenotypeBehavior.cpp',
               'src/Population.cpp',
               'src/Random.cpp',
               'src/Species.cpp',
               'src/Substrate.cpp',
               'src/Utils.cpp']

    extra = ['-march=native',
             '-mtune=native',
             '-g',
             ]

    if platform == 'darwin':
        extra += ['-stdlib=libc++',
             '-std=c++11',]
    else:
        extra += ['-std=gnu++11']

    is_windows = 'win' in platform and platform != 'darwin'
    if is_windows:
        extra.append('/EHsc')
    else:
        extra.append('-w')

    prefix = os.getenv('PREFIX')
    if prefix and len(prefix) > 0:
        extra += ["-I{}/include".format(prefix)]

    build_sys = os.getenv('MN_BUILD')

    if build_sys is None:
        if os.path.exists('_MultiNEAT.cpp'):
            sources.insert(0, '_MultiNEAT.cpp')
            extra.append('-O3')
            extensionsList.extend([Extension('MultiNEAT._MultiNEAT',
                                             sources,
                                             extra_compile_args=extra)],
                                  )
            build_sys='cython_pre'
        else:
            print('Source file is missing and MN_BUILD environment variable is not set.\n'
                  'Specify either \'cython\' or \'boost\'. Example to build in Linux with Cython:\n'
                  '\t$ export MN_BUILD=cython')
            s = input('Enter "c" for cython, "b" for boost, or anything else to quit\n')
            if s == 'c':
                build_sys = 'cython'
            elif s == 'b':
                build_sys = 'boost'
            else:
                exit(1)

    if build_sys == 'cython':
        from Cython.Build import cythonize
        sources.insert(0, '_MultiNEAT.pyx')
        extra.append('-O3')
        # For Windows using Boost - change to location of Boost libs
        if is_windows:
            extra += ["-I{}\\".format('C:\\local\\boost_1_72_0')]
        extensionsList.extend(cythonize([Extension('MultiNEAT._MultiNEAT',
                                                   sources,
                                                   extra_compile_args=extra)],
                                        ))
    elif build_sys == 'boost':
        is_python_2 = sys.version_info[0] < 3

        sources.insert(0, 'src/PythonBindings.cpp')

        if is_windows:
            if is_python_2:
                raise RuntimeError("Python prior to version 3 is not supported on Windows due to limits of VC++ compiler version")

        lib_dirs = []

        BOOST_SYSTEM = 'boost_system'
        BOOST_SERIAL = 'boost_serialization'
        BOOST_PYTHON = 'boost_python'
        BOOST_NUMPY = 'boost_numpy'
        BOOST_LIBS_VERS_STRING = ""

        # Change to your version of Python
        if not is_python_2:
            # with boost 1.67 you need boost_python3x and boost_numpy3x where x is python version 3.x
            # in Ubuntu 14 there is only 'boost_python-py34'
            BOOST_PYTHON += "38"
            BOOST_NUMPY += "38"

        # For Windows with mingw
        # libraries= ['libboost_python-mgw48-mt-1_58',
        #           'libboost_serialization-mgw48-mt-1_58'],
        # include_dirs = ['C:\Program Files\mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\include', 'C:\local\boost_1_72_0'],
        # lib_dirs += ['C:\Program Files\mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\lib', 'C:\local\boost_1_72_0\lib32-msvc-14.1'],

        # For Windows using MSVC / Boost - change to location of Boost libs, correct Boost/MSVC version, and architecture (x86 or x64)
        if is_windows:
            extra += ["-I{}\\".format('C:\\local\\boost_1_72_0')]
            lib_dirs += ['C:\\local\\boost_1_72_0\\stage\\lib64-msvc-14.1\\lib']
            BOOST_LIBS_VERS_STRING = "-vc141-mt-x64-1_72"
            BOOST_PYTHON = "lib" + BOOST_PYTHON
            BOOST_NUMPY = "lib" + BOOST_NUMPY

        BOOST_SYSTEM += BOOST_LIBS_VERS_STRING
        BOOST_SERIAL += BOOST_LIBS_VERS_STRING
        BOOST_PYTHON += BOOST_LIBS_VERS_STRING
        BOOST_NUMPY += BOOST_LIBS_VERS_STRING

        libs = [BOOST_SYSTEM, BOOST_SERIAL, BOOST_PYTHON, BOOST_NUMPY]

        extra.extend(['-DUSE_BOOST_PYTHON', '-DUSE_BOOST_RANDOM', #'-O0',
                      #'-DVDEBUG',
                      ])
        exx = Extension('MultiNEAT._MultiNEAT',
                        sources,
                        libraries=libs,
                        library_dirs=lib_dirs,
                        extra_compile_args=extra)
        print(dir(exx))
        print(exx)
        print(exx.extra_compile_args)
        extensionsList.append(exx)
    elif build_sys == 'cython_pre':
        pass
    else:
        raise AttributeError('Unknown tool: {}'.format(build_sys))

    return extensionsList


setup(name='multineat',
      version='0.5', # Update version in conda/meta.yaml as well
      packages=['MultiNEAT'],
      ext_modules=getExtensions())
