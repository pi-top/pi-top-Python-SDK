=====================================================
pi-top Python SDK
=====================================================

.. image:: https://badge.fury.io/gh/pi-top%2Fpitop.svg
    :target: https://badge.fury.io/gh/pi-top%2Fpitop
    :alt: Source code on GitHub

A simple, modular interface for interacting with a pi-top and its related accessories and components.

.. image:: docs/_static/pi_top_4.png

-----
About
-----

This library is installed as a Python 3 module called `pitop`. It includes several
submodules that allow you to easily interact with most of the hardware inside a pi-top.

This repository also contains CLI utilities, to communicate with your pi-top using the terminal.

See the `Recipes`_ chapter of the documentation for ideas on how to get started.

.. _Recipes: https://pitop.readthedocs.io/en/stable/recipes.html

-----------
Usage
-----------

You can easily connect different components of the system using the
modules available in the library:

.. code-block: python

    from time import sleep
    from pitop.pma import UltrasonicSensor
    from pitop.oled import PTOLEDDisplay

    oled = PTOLEDDisplay()
    utrasonic = PMAUltrasonicSensor("D1")

    while True:
        distance = utrasonic.distance
        oled.draw_multiline_text(str(distance))
        sleep(0.1)


Same with the provided CLI utilities:

... code-block: bash
    pt-oled "Hey! I'm a $(pt-host)"

-------------
Requirements
-------------

The following packages are required in your device for this library to work.

.. table::
    :widths: 30 70

    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | Package Name              | Usage                                                                                                                 |
    +===========================+=======================================================================================================================+
    | ``alsa-utils``            | Used for configuring the system audio; such as setting the correct audio card when connecting a pi-topSPEAKER.        |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``coreutils``             | Used to perform basic OS operations and commands; such as ``ls`` and ``chmod``                                        |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``fonts-droid-fallback``  | Minimum essential font used by the OLED screen.                                                                       |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``i2c-tools``             | Communicate with pi-top I2C devices.                                                                                  |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``pt-device-manager``     | Allows communication with pi-top's hub; such as getting battery state.                                                |
    |                           | This package installs a ``systemd`` service that needs to be running for this library to work properly                |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+
    | ``raspi-config``          | Required to communicate and set parameters to the Raspberry Pi.                                                       |
    +---------------------------+-----------------------------------------------------------------------------------------------------------------------+

-------------
Installation
-------------

The pi-top Python SDK is installed out of the box with pi-topOS, which is available from
pi-top.com_. To install on Raspberry Pi OS or other operating systems, see the `Installing`_ chapter.

.. _pi-top.com: https://www.pi-top.com/products/os/
.. _Installing: https://pitop.readthedocs.io/en/stable/installing.html

-------------
Documentation
-------------

Comprehensive documentation is available at https://pitop.readthedocs.io/.
Please refer to the `Contributing`_ and `Development`_ chapters in the
documentation for information on contributing to the project.

.. _Contributing: https://pitop.readthedocs.io/en/stable/contributing.html
.. _Development: https://pitop.readthedocs.io/en/stable/development.html

-------------
Contributors
-------------

See the `contributors page`_ on GitHub for more info.

.. _contributors page: https://github.com/pi-top/pitop/graphs/contributors
