import os
import subprocess
from enum import Enum

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils.build_ext import new_build_ext as build_ext
from distutils.command.install import install
from distutils.command.build import build

# name of Interfacing API
APPNAME = "PySolverInterface"

PYTHON_BINDINGS_PATH = os.path.dirname(os.path.abspath(__file__))
PRECICE_ROOT = os.environ['PRECICE_ROOT']
PRECICE_BUILD = os.environ['PRECICE_BUILD']
PRECICE_MPI_COMPILER = os.environ['PRECICE_MPI_COMPILER']

try:
    os.chdir(PRECICE_ROOT)
except TypeError:
    print("The preCICE root directory is not defined. Have you set the $PRECICE_ROOT environment variable?")
    sys.exit(1)
except FileNotFoundError:
    print("$PRECICE_ROOT directory does not exist. Please set the $PRECICE_ROOT environment variable to a valid directory.")
    sys.exit(1)

try:
    os.chdir(PRECICE_BUILD)
except TypeError:
    print("The preCICE build directory is not defined. Have you set the $PRECICE_BUILD environment variable?")
    sys.exit(1)
except FileNotFoundError:
    print("$PRECICE_BUILD directory does not exist. Please set the $PRECICE_BUILD environment variable to a valid directory.")
    sys.exit(1)


class MpiImplementations(Enum):
    OPENMPI = 1
    MPICH = 2


def check_mpi_implementation(mpi_compiler_wrapper):
    FNULL = open(os.devnull, 'w')  # used to supress output of subprocess.call

    if subprocess.call([mpi_compiler_wrapper,"-showme:compile"], stdout=FNULL, stderr=FNULL) == 0:
        PRECICE_MPI_IMPLEMENTATION = MpiImplementations.OPENMPI
    elif subprocess.call([mpi_compiler_wrapper,"-compile-info"], stdout=FNULL, stderr=FNULL) == 0:
        PRECICE_MPI_IMPLEMENTATION = MpiImplementations.MPICH
    else:
        raise Exception("unknown/no mpi++")

    return PRECICE_MPI_IMPLEMENTATION


def determine_mpi_args(mpi_compiler_wrapper):
    PRECICE_MPI_IMPLEMENTATION = check_mpi_implementation(mpi_compiler_wrapper)
    # determine which flags to use with mpi compiler wrapper
    if PRECICE_MPI_IMPLEMENTATION is MpiImplementations.OPENMPI:
        mpi_compile_args = subprocess.check_output([mpi_compiler_wrapper, "-showme:compile"]).decode().strip().split(
            ' ')
        mpi_link_args = subprocess.check_output([mpi_compiler_wrapper, "-showme:link"]).decode().strip().split(' ')
    elif PRECICE_MPI_IMPLEMENTATION is MpiImplementations.MPICH:
        mpi_compile_args = subprocess.check_output([mpi_compiler_wrapper, "-compile-info"]).decode().strip().split(' ')[
                           1::]
        mpi_link_args = subprocess.check_output([mpi_compiler_wrapper, "-link-info"]).decode().strip().split(' ')[1::]
    else:  # if PRECICE_MPI_IMPLEMENTATION is not mpich or openmpi quit.
        raise Exception("unknown/no mpi found using compiler %s. Could not build PySolverInterface." % mpi_compiler_wrapper)

    return mpi_compile_args, mpi_link_args


def get_extensions(mpi_compiler_wrapper, precice_buildfolder):
    mpi_compile_args, mpi_link_args = determine_mpi_args(mpi_compiler_wrapper)

    # need to include libs here, because distutils messes up the order
    compile_args = ["-I" + PRECICE_ROOT, "-Wall", "-std=c++11"] + mpi_compile_args
    link_args = ["-L" + precice_buildfolder, "-lprecice"] + mpi_link_args

    return [
        Extension(
                APPNAME,
                sources=[os.path.join(PYTHON_BINDINGS_PATH, APPNAME) + ".pyx"],
                libraries=[],
                include_dirs=[PRECICE_ROOT],
                language="c++",
                extra_compile_args=compile_args,
                extra_link_args=link_args
            )
    ]

class my_build_ext(build_ext, object):     
    def finalize_options(self):
        if not self.distribution.ext_modules:
            print("adding extension")
            self.distribution.ext_modules = get_extensions(PRECICE_MPI_COMPILER, PRECICE_BUILD)

        print("#####")
        super(my_build_ext, self).finalize_options()


class my_build(build, object):
    def finalize_options(self):
        if not self.distribution.ext_modules:
            print("adding extension")
            self.distribution.ext_modules = get_extensions(PRECICE_MPI_COMPILER, PRECICE_BUILD)

        print("#####")

        super(my_build, self).finalize_options()       


# build precice.so python extension to be added to "PYTHONPATH" later
setup(
    name=APPNAME,
    description='Python language bindings for preCICE coupling library',
    cmdclass={'build_ext': my_build_ext,
              'build': my_build,
              'install': install}
)
