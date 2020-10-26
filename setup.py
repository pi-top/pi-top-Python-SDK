"A simple interface to GPIO devices with Raspberry Pi."

import io
import os
import sys
import errno
from setuptools import setup, find_packages

if sys.version_info[0] == 3:
    if not sys.version_info >= (3, 2):
        raise ValueError('This package requires Python 3.2 or above')
else:
    raise ValueError('Unrecognized major version of Python')

HERE = os.path.abspath(os.path.dirname(__file__))

# Workaround <http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html>
try:
    import multiprocessing
except ImportError:
    pass

with open(os.path.abspath('debian/changelog')) as f:
    first_line = f.readline()

__project__ = first_line.split(" ")[0]
__version__ = first_line.split(" ")[1].replace("(", "").replace(")", "")
project = 'pi-top Maker Architecture (PMA) Components'
# TODO: get from trailer line in changelog?
__author__ = 'pi-top'
__author_email__ = 'deb-maintainers@pi-top.com'

assert __project__ != ""
assert __version__ != ""

__url__ = 'https://github.com/pi-top/pi-top-Maker-Architecture'
__platforms__ = 'ALL'

__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Intended Audience :: Developers",
    "Topic :: Education",
    "Topic :: System :: Hardware",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: PyPy",
]

__keywords__ = [
    'pi-top',
    'raspberrypi',
    'gpio',
]

__requires__ = [
    # To use GPIO & components
    'gpiozero',
    # To perform operations with images
    "imageio",
    # Camera uses numpy arrays for image data
    "numpy",
    # Manage camera images
    "Pillow",
    # Common functions
    "ptcommon",
    # Camera communication
    "PyV4L2Camera",
]

__extra_requires__ = {
    'doc':   ['sphinx'],
    'test':  ['pytest', 'coverage', 'mock'],
}

if sys.version_info[:2] == (3, 2):
    # Particular versions are required for Python 3.2 compatibility
    __extra_requires__['doc'].extend([
        'Jinja2<2.7',
        'MarkupSafe<0.16',
    ])
    __extra_requires__['test'][0] = 'pytest<3.0dev'
    __extra_requires__['test'][1] = 'coverage<4.0dev'
elif sys.version_info[:2] == (3, 3):
    __extra_requires__['test'][0] = 'pytest<3.3dev'
elif sys.version_info[:2] == (3, 4):
    __extra_requires__['test'][0] = 'pytest<5.0dev'

__entry_points__ = {}


def main():
    import io
    with io.open(os.path.join(HERE, 'README.rst'), 'r') as readme:
        setup(
            name=__project__,
            version=__version__,
            description=__doc__,
            long_description=readme.read(),
            classifiers=__classifiers__,
            author=__author__,
            author_email=__author_email__,
            url=__url__,
            license=[
                c.rsplit('::', 1)[1].strip()
                for c in __classifiers__
                if c.startswith('License ::')
            ][0],
            keywords=__keywords__,
            packages=find_packages(),
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
            extras_require=__extra_requires__,
            entry_points=__entry_points__,
        )


if __name__ == '__main__':
    main()
