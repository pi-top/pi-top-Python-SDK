"""pi-top Python SDK."""

import os
import sys

from setuptools import setup

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = os.environ.get("CURRENT_VERSION")
assert __version__ != ""

__project__ = "pitop.processing"
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
]

__requires__ = [
    f"pitop.common=={__version__}",
    f"pitop.pma=={__version__}",
    f"pitop.core=={__version__}",
    "numpy>=1.16.0,<1.17",
    "imutils>=0.5.4,<0.6.0",
    "matplotlib>=3.0.0,<3.1",
    "onnxruntime>=1.7.2,<1.9",
    "wget>=3.2,<4.0",
    #############################
    # Advanced image processing #
    #############################
    "dlib>=19.22.0,<19.23.0",
    "scikit-learn>=0.20.2,<0.21.0",
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
            packages=["pitop.processing"],
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
        )


if __name__ == "__main__":
    main()
