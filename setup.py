#!/usr/bin/env python

# PyLPSolve is an object oriented wrapper for the open source LP
# solver lp_solve. Copyright (C) 2010 Hoyt Koepke.
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

################################################################################
# All the control parameters should go here

import os
import sys
from glob import glob
from itertools import chain

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
from distutils.extension import Extension


VERSION = "0.2.0"

NAME = 'pylpsolve'
DESCRIPTION = "PyLPSolve: Object-oriented wrapper for the lpsolve linear programming solver."

DESCRIPTION_LONG = \
"""
PyLPSolve is an object oriented wrapper for the open source LP solver
lpsolve.  The focus is on usability and integration with existing
python packages used for scientific programming (i.e. numpy and
scipy).

One unique feature is a convenient bookkeeping system that allows the
user to specifiy blocks of variables by string tags, or other index
block methods, then work with these blocks instead of individual
indices.  All the elements of the LP are cached until solve is called,
with memory management and proper sizing of the LP in lpsolve handled
automatically.

PyLPSolve is written in cython, with all low-level processing done
effectively in low-level C for speed.  Thus there should be mimimal
overhead to using this wrapper.

While lpsolve is licensed under the LGPLv2 license, the PyLPSolve
wrapper library is licensed under the liberal BSD license to encourage
reuse with other LP solvers.
"""

AUTHOR = "Hoyt Koepke"
AUTHOR_EMAIL = "hoytak@gmail.com"
SCRIPTS = []
URL = ""
URL_DOWNLOAD = ""

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Cython',
    'Programming Language :: C'
]

DEBUG_C = False

NUMPY = True

SOURCE_DIR = ['pylpsolve']

LPSOLVE_BASE = 'pylpsolve/lp_solve_5.5'

# Stuff for extension modules
SOURCES_EXTRA = {'pylpsolve.pylpsolve' : [os.path.join(LPSOLVE_BASE, f) for f in 
                                          ['lp_MDO.c', 'shared/commonlib.c', 'shared/mmio.c', 'shared/myblas.c', 
                                           'ini.c', 'fortify.c', 'colamd/colamd.c', 'lp_rlp.c', 'lp_crash.c', 
                                           'bfp/bfp_LUSOL/lp_LUSOL.c', 'bfp/bfp_LUSOL/LUSOL/lusol.c', 'lp_Hash.c', 
                                           'lp_lib.c', 'lp_wlp.c', 'lp_matrix.c', 'lp_mipbb.c', 'lp_MPS.c', 'lp_params.c', 
                                           'lp_presolve.c', 'lp_price.c', 'lp_pricePSE.c', 'lp_report.c', 'lp_scale.c', 
                                           'lp_simplex.c', 'lp_SOS.c', 'lp_utils.c', 'yacc_read.c']]}

COMPILER_ARGS = ['-O3', '-DYY_NEVER_INTERACTIVE','-DPARSER_LP', '-DINVERSE_ACTIVE=INVERSE_LUSOL', '-DRoleIsExternalInvEngine']
LINK_ARGS = ['-O3']

include_dirs_extra = [os.path.join(LPSOLVE_BASE, d) for d in ['.', 'shared', 'bfp', 'bfp/bfp_LUSOL', 'bfp/bfp_LUSOL/LUSOL', 'colamd']]
library_dirs_extra = []

library_includes = []
library_specific = {}


if NUMPY:
    import numpy
    include_dirs_extra.append(numpy.get_include())


# First, see if we're authorized to use cython files, or if we should instead compile the included files
if "--cython" in sys.argv:
    cython_mode = True
    del sys.argv[sys.argv.index("--cython")]
else:
    cython_mode = False

# Get all the cython files in the sub directories and in this directory
if cython_mode:
    cython_files = dict( (d, glob(os.path.join(d, "*.pyx"))) for d in SOURCE_DIR + ['.'])
else:
    cython_files = {}

cython_files_all = set(chain(*cython_files.values()))

if cython_mode:
    print("Cython Files Found: \n%s" % ", ".join(sorted(cython_files_all)))
else:
    print("Cython support disabled; compiling extensions from pregenerated C sources.")
    print("To enable cython, run setup.py with the option --cython.")


# Set the compiler arguments -- Add in the environment path stuff
ld_library_path = os.getenv("LD_LIBRARY_PATH")

if ld_library_path is not None:
    lib_paths = ld_library_path.split(":")
else:
    lib_paths = []

include_path = os.getenv("INCLUDE_PATH")
if include_path is not None:
    include_paths = [p.strip() for p in include_path.split(":") if len(p.strip()) > 0]
else:
    include_paths = []

# get all the c files that are not cythonized .pyx files.
c_files   = dict( (d, [f for f in glob(os.path.join(d, "*.c"))
                       if (f[:-2] + '.pyx') not in cython_files_all])
                  for d in SOURCE_DIR + ['.'])

for d, l in chain(((d, glob(os.path.join(d, "*.cxx"))) for d in SOURCE_DIR + ['.']),
                  ((d, glob(os.path.join(d, "*.cpp"))) for d in SOURCE_DIR + ['.'])):
    c_files[d] += l

print("C Extension Files Found: \n%s" % ", ".join(sorted(chain(*c_files.values()))))


# Collect all the python modules
def get_python_modules(f):
    d, m = os.path.split(f[:f.rfind('.')])
    return m if len(d) == 0 else d + "." + m

exclude_files = set(["setup.py"])
python_files = set(chain(* (list(glob(os.path.join(d, "*.py")) for d in SOURCE_DIR) + [glob("*.py")]))) 
python_files -= exclude_files

python_modules = [get_python_modules(f) for f in python_files]

print("Relevant Python Files Found: \n%s" % ", ".join(sorted(python_files)))


def get_defined_macros(m):
    return [('WIN32', '1')] if os.name == 'nt' else []

def get_include_dirs(m):
    return [l.strip() for l in include_dirs_extra + include_paths
            if len(l.strip()) != 0]

def get_library_dirs(m):
    return [l.strip() for l in library_dirs_extra + lib_paths
            if len(l.strip()) != 0]

def get_libraries(m):
    return library_includes + (library_specific[m] if m in library_specific else [])

def get_extra_compile_args(m):
    return COMPILER_ARGS + (['-g', '-O0', '-DCYTHON_REFNANNY'] if DEBUG_C else [])

def get_extra_link_args(m):
    return LINK_ARGS + (['-g'] if DEBUG_C else [])

def get_extra_source_files(m):
    return SOURCES_EXTRA[m] if m in SOURCES_EXTRA else []

def get_cython_extensions(d, filelist):
    ext_modules = []

    for f in filelist:
        f_no_ext = f[:f.rfind('.')]
        f_mod = os.path.split(f_no_ext)[1]
        modname = "%s.%s" % (d, f_mod) if d != '.' else f_mod
        
        ext_modules.append(Extension(
            modname,
            [f] + get_extra_source_files(modname),
            define_macros = get_defined_macros(modname),
            include_dirs = get_include_dirs(modname),
            library_dirs = get_library_dirs(modname),
            libraries = get_libraries(modname),
            extra_compile_args = get_extra_compile_args(modname),
            extra_link_args = get_extra_link_args(modname),
        ))

    return ext_modules

ext_modules = []

if cython_mode:
    from Cython.Distutils import build_ext #@UnresolvedImport

    ext_modules += list(chain(*list(get_cython_extensions(d, l) for d, l in cython_files.items())))
    
    cmdclass = {'build_ext' : build_ext}
else:
    cmdclass = {}

ext_modules += list(chain(*list(get_cython_extensions(d, l) for d, l in c_files.items())))

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = DESCRIPTION_LONG,
    author = AUTHOR, 
    author_email = AUTHOR_EMAIL,
    cmdclass = cmdclass,
    ext_modules = ext_modules,
    py_modules = python_modules,
    scripts = SCRIPTS,
    classifiers = CLASSIFIERS,
    url = URL,
    download_url = URL_DOWNLOAD
)
