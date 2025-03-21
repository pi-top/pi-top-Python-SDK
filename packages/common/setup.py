"""Pi-top Python SDK."""

import os
import sys

from setuptools import setup

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = os.environ.get("PYTHON_PACKAGE_VERSION", "0.0.1.dev1").replace('"', "")
assert __version__ != ""

__project__ = "pitop.common"
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
    # For reviewing DHCP leases
    "isc_dhcp_leases>=0.9.1,<1.0.0",
    # For network interface checking
    "netifaces>=0.10.4,<1.0.0",
    # For journal logging
    "systemd-python",
    # SMBusDevice (PMA)
    "smbus2>=0.4.0,<1.0.0",
    # Device Communication
    "pyzmq>=20.0.0,<25.0.0",
    # To determine boot partition mount point
    "psutil",
    # For flask sockets
    "werkzeug",
    "gevent-websocket",
]


def main():
    import io

    with io.open(os.path.join(HERE, "README.rst"), "r") as readme:
        setup(
            name=__project__,
            version=__version__,
            description=__doc__,
            long_description=readme.read(),
            long_description_content_type="text/markdown",
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
            packages=["pitop.common"],
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
        )


if __name__ == "__main__":
    main()
