"""pi-top Python SDK."""

import os
import sys

from setuptools import setup

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = os.environ.get("PYTHON_PACKAGE_VERSION", "0.0.1.dev1")
assert __version__ != ""

__project__ = "pitop.keyboard"
__author__ = "pi-top"
__author_email__ = "deb-maintainers@pi-top.com"

__url__ = "https://github.com/pi-top/pi-top-Python-SDK"
__platforms__ = "ALL"

# https://pypi.org/classifiers/
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Intended Audience :: Developers",
    "Topic :: Education",
    "Topic :: System :: Hardware",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: PyPy",
]

__keywords__ = [
    "pi-top",
    "raspberrypi",
    "battery",
    "xlib>=0.17",
]

__requires__ = [
    f"pitop.common=={__version__}",
]


def main():
    import io

    with io.open(os.path.join(HERE, "README.rst"), "r") as readme:
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
                c.rsplit("::", 1)[1].strip()
                for c in __classifiers__
                if c.startswith("License ::")
            ][0],
            keywords=__keywords__,
            packages=["pitop.keyboard"],
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
        )


if __name__ == "__main__":
    main()
