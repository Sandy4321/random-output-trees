# Authors: Arnaud Joly <arnaud.v.joly@gmail.com>
#
# License: BSD 3 clause

import os


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    import numpy

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config = Configuration('random_output_trees', parent_package,
                           top_path)



    for module in ["_tree", "_sklearn_tree", "_sklearn_tree_utils"]:
        config.add_extension(module,
                             sources=["%s.c" % module],
                             include_dirs=[numpy.get_include()],
                             libraries=libraries,
                             extra_compile_args=["-O3"])


    # add the test directory
    config.add_subpackage('tests')

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
