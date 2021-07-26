"""pi-top Python SDK."""

import os
import sys
from setuptools import setup, find_packages

if not sys.version_info >= (3, 7):
    raise ValueError("This package requires Python 3.7 or above")

HERE = os.path.abspath(os.path.dirname(__file__))

# Workaround <http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html>
try:
    import multiprocessing  # noqa: F401, lgtm[py/unused-import]
except ImportError:
    pass

with open(os.path.join(HERE, "debian/rules")) as search:
    for line in search:
        if "export PYBUILD_NAME=" in line:
            __project__ = line.split("=")[1].rstrip()
            break

assert __project__ != ""

# Get first field of the changelog
with open(os.path.join(HERE, "debian/changelog")) as f:
    first_line_changelog = f.readline()

# Get Debian version from first field; strip surrounding brackets
debian_version = first_line_changelog.split(" ")[1].rstrip()[1:-1]

# Convert Debian version to Python version
python_version = debian_version
for r in (
    ("(", ""),
    (")", ""),

    # Convert from gbp version format to PEP 440 local version format:
    # (replace '~' with '+')
    # See https://www.python.org/dev/peps/pep-0440/#local-version-identifiers for more information
    ("~", "+"),
):
    python_version = python_version.replace(*r)

__version__ = python_version
assert __version__ != ""

project = "pi-top Python SDK"
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
    ####################################
    # Utilities - functions, IDs, etc. #
    ####################################
    "pitopcommon==0.8.8",

    #######
    # PMA #
    #######
    # To use GPIO & components
    "gpiozero==1.6.2",
    # To perform operations with images
    "imageio==2.4.1",
    # Camera uses numpy arrays for image data
    "numpy==1.16.6",
    # Manage camera images
    "Pillow==5.4.1",
    # Camera communication
    "PyV4L2Camera==0.1a2",
    # IMU Calibration
    "matplotlib==3.0.2",
    "scipy==1.1.0",

    ############
    # Keyboard #
    ############
    "pynput==1.4.2",

    ########
    # OLED #
    ########
    "luma.core==2.3.1",
    "luma.oled==3.8.1",
    "monotonic==1.1",
    "pyinotify==0.9.6",

    #########
    # Pulse #
    #########
    "pyserial==3.4",

    ##############
    # Algorithms #
    ##############
    "simple_pid==0.2.4",

    #############
    # Webserver #
    #############
    "flask==1.0.2",
    "flask-cors==3.0.7",
    "flask-sockets==0.2.1",
    "gevent==1.3.7",
    "gevent-websocket==0.10.1",

    #############################
    # Advanced image processing #
    #############################
    "dlib==19.22.0",
    "imutils==0.5.4",
    "scikit-learn==0.20.2",

    ###################
    # Use Model Files #
    ###################
    "onnxruntime==1.8.1",

    ########################
    # Download Model Files #
    ########################
    "wget==3.2",
]

__extra_requires__ = {
    "computer_vision": ["opencv"],
    "doc": ["sphinx"],
}

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
            packages=find_packages(),
            include_package_data=True,
            platforms=__platforms__,
            install_requires=__requires__,
            extras_require=__extra_requires__,
            entry_points=__entry_points__,
        )


if __name__ == "__main__":
    main()
