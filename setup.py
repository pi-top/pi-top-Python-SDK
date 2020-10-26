"A simple interface to GPIO devices with Raspberry Pi."

import io
import os
import sys
import errno
from setuptools import setup, find_packages

if sys.version_info[0] == 2:
    if not sys.version_info >= (2, 7):
        raise ValueError('This package requires Python 2.7 or above')
elif sys.version_info[0] == 3:
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

__project__ = 'ptpma'
__version__ = '2.1.0'
__author__ = 'Mike Roberts'
__author_email__ = 'mike@pi-top.com'
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

__entry_points__ = {
    #     'gpiozero_pin_factories': [
    #         'pigpio  = gpiozero.pins.pigpio:PiGPIOFactory',
    #         'rpigpio = gpiozero.pins.rpigpio:RPiGPIOFactory',
    #         'rpio    = gpiozero.pins.rpio:RPIOFactory',
    #         'native  = gpiozero.pins.native:NativeFactory',
    #         'mock    = gpiozero.pins.mock:MockFactory',
    #         # Backwards compatible names
    #         'PiGPIOPin  = gpiozero.pins.pigpio:PiGPIOFactory',
    #         'RPiGPIOPin = gpiozero.pins.rpigpio:RPiGPIOFactory',
    #         'RPIOPin    = gpiozero.pins.rpio:RPIOFactory',
    #         'NativePin  = gpiozero.pins.native:NativeFactory',
    #     ],
    #     'gpiozero_mock_pin_classes': [
    #         'mockpin          = gpiozero.pins.mock:MockPin',
    #         'mockpwmpin       = gpiozero.pins.mock:MockPWMPin',
    #         'mockchargingpin  = gpiozero.pins.mock:MockChargingPin',
    #         'mocktriggerpin   = gpiozero.pins.mock:MockTriggerPin',
    #     ]
}


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
