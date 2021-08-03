"""pi-top Python SDK."""

import os
import sys

from setuptools import find_packages, setup

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = os.environ.get("CURRENT_VERSION")
assert __version__ != ""

__project__ = "pitop"
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
    "gpio",
]

__extra_requires__ = {
    "computer_vision": ["opencv"],
    "doc": ["sphinx"],
}

__requires__ = [
    ###############
    # Subpackages #
    ###############
    f"pitop.common=={__version__}",
    f"pitop.system=={__version__}",
    f"pitop.core=={__version__}",
    f"pitop.pma=={__version__}",
    f"pitop.camera=={__version__}",
    f"pitop.keyboard=={__version__}",
    f"pitop.robotics=={__version__}",
    f"pitop.processing=={__version__}",
    #########
    # PROTO #
    #########
    # To use GPIO & components
    "gpiozero>=1.6.2,<1.7",
    #########
    # Pulse #
    #########
    "pyserial>=3.4,<3.5",
    #############
    # Webserver #
    #############
    "flask>=1.0.2,<1.1",
    "flask-cors>=3.0.7,<3.1",
    "flask-sockets>=0.2.1,<0.3",
    "gevent>=1.3.7,<1.4",
    "gevent-websocket>=0.10.1,<0.11.0",
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
            packages=find_packages(),
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
            extras_require=__extra_requires__,
        )


if __name__ == "__main__":
    main()
