"""Pi-top Python SDK."""

import os
import sys

from setuptools import setup

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = os.environ.get("PYTHON_PACKAGE_VERSION", "0.0.1.dev1").replace('"', "")
assert __version__ != ""

__project__ = "pitopcli"
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

__requires__ = [
    f"pitop.common=={__version__}",
    f"pitop.battery=={__version__}",
    f"pitop.system=={__version__}",
    f"pitop.display=={__version__}",
    f"pitop.pma=={__version__}",
    f"pitop.miniscreen=={__version__}",
    "netifaces>=0.10.4,<1.0.0",
    "numpy>1.19.5,<2.0.0",
    "numpy>1.19.5,<2.0.0",
    "matplotlib>=3.3.4,<4.0.0",
    "scipy>=1.6.0,<2.0",
]


__entry_points__ = {
    "console_scripts": [
        # 'pt' shortened command
        "pt=pitopcli.pitop:main",
        # 'pi-top' longhand/easy-to-remember command
        "pi-top=pitopcli.pitop:main",
    ]
}


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
            packages=["pitopcli"],
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
            entry_points=__entry_points__,
        )


if __name__ == "__main__":
    main()
