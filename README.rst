===========================
pi-top Python SDK (Preview)
===========================

A simple, modular interface for interacting with a pi-top and its related accessories and components.

.. ###############################################
.. # NOTE: THESE ARE EXTERNAL LINKS, AS THEY ARE #
.. # REQUIRED FOR THE IMAGES TO SHOW ON PYPI     #
.. ###############################################

Supports all pi-top devices:

.. image:: https://github.com/pi-top/pi-top-Python-SDK/raw/master/docs/_static/overview/devices.jpg

Supports pi-top Maker Architecture (PMA):

.. image:: https://github.com/pi-top/pi-top-Python-SDK/raw/master/docs/_static/overview/pma.jpg

Supports all pi-top peripherals:

.. image:: https://github.com/pi-top/pi-top-Python-SDK/raw/master/docs/_static/overview/peripherals.jpg

--------------------------
Status: Active Development
--------------------------

This SDK is currently in active development. Please be patient while we work towards v1.0.0!

Backwards Compatibility
=======================

When this library reaches v1.0.0, we will aim to maintain backwards-compatibility thereafter. Until then, every effort will be made to ensure stable support, but it cannot be guaranteed. Breaking changes will be clearly documented.

--------------------
Build Status: Latest
--------------------

.. image:: https://img.shields.io/github/workflow/status/pi-top/pi-top-Python-SDK/Build,%20Test%20and%20Publish
   :alt: GitHub Workflow Status


.. image:: https://img.shields.io/github/v/tag/pi-top/pi-top-Python-SDK
    :alt: GitHub tag (latest by date)

.. image:: https://img.shields.io/github/v/release/pi-top/pi-top-Python-SDK
    :alt: GitHub release (latest by date)

.. image:: https://img.shields.io/pypi/v/pitop
   :alt: PyPI release

.. image:: https://readthedocs.com/projects/pi-top-pi-top-python-sdk/badge/?version=latest&token=13589f150cf192dcfc6ebfd53aae33164450aafd181c5e49018a21fd93149127
    :target: https://docs.pi-top.com/python-sdk/latest/?badge=latest
    :alt: Documentation Status

-----
About
-----

This SDK aims to provide an easy-to-use framework for managing a pi-top. It includes a Python 3 package (`pitop`),
with several modules for interfacing with a range of pi-top devices and peripherals It also contains CLI utilities,
to interact with your pi-top using the terminal.

The SDK is included out-of-the-box with pi-topOS.

Ensure that you keep your system up-to-date to enjoy the latest features and bug fixes.

This library is installed as a Python 3 module called `pitop`. It includes several
submodules that allow you to easily interact with most of the hardware inside a pi-top.

You can easily connect different components of the system using the
modules available in the library:


.. code-block:: python

    from time import sleep
    from pitop.pma import UltrasonicSensor
    from pitop.miniscreen import OLED

    oled = OLED()
    utrasonic = PMAUltrasonicSensor("D1")

    while True:
        distance = utrasonic.distance
        oled.display_multiline_text(str(distance))
        sleep(0.1)

Check out the `API Recipes`_ chapter of the documentation for ideas on how to get started.

.. _API Recipes: https://docs.pi-top.com/python-sdk/en/stable/recipes_api.html


This repository also contains a 'pi-top' command-line interface (CLI) for some SDK functionality:

.. code-block:: bash

    $ pi-top oled write "Hey! I'm a $(pt devices hub)"


A 'pt' alias is also provided for quicker typing:

.. code-block:: bash

    $ pt oled write "Hey! I'm a $(pt devices hub)"

Check out the `CLI`_ chapter of the documentation for ideas on how to get started.

.. _CLI: https://docs.pi-top.com/python-sdk/en/stable/cli_tools.html

------------
Installation
------------

The pi-top Python SDK is installed out of the box with pi-topOS, which is available from
pi-top.com_. To install on Raspberry Pi OS or other operating systems, see the `Getting Started`_ chapter.

.. _pi-top.com: https://www.pi-top.com/products/os/
.. _Getting Started: https://docs.pi-top.com/python-sdk/en/stable/getting_started.html

-------------
Documentation
-------------

Comprehensive documentation is available here_.

.. _here: https://docs.pi-top.com/python-sdk/

-------------
Development
-------------

To make changes to the SDK you'll want to install it from source with the
documentation and test dependencies:

.. code-block:: bash

    git clone https://github.com/pi-top/pi-top-Python-SDK.git
    cd pi-top-Python-SDK
    pip3 install -e ".[doc,test]"


Changes you make to the source will be reflected in your Python environment.

You may want to repeat this process for the pi-top-Python-Common-Library_ if
it's not installed already or you need to make changes there too.

.. _pi-top-Python-Common-Library: https://github.com/pi-top/pi-top-Python-Common-Library

Once the SDK is installed you can run the automated test suite with:

.. code-block:: bash

    python3 -m pytest

And you can build the docs locally by running:

.. code-block:: bash

    PYTHONPATH=. sphinx-build -W -v -bhtml docs/ build/html

To view the generated docs open the `build/html/index.html` file in your browser.

Most of the SDK requires pi-top hardware to work but it should be possible to
run the tests and build documentation in any environment with Python3.

------------
Contributing
------------

Please refer to the `Contributing`_ document in this repository
for information on contributing to the project.

.. _Contributing: https://github.com/pi-top/pi-top-Python-SDK/blob/master/.github/CONTRIBUTING.md

See the `contributors page`_ on GitHub for more info on contributors.

.. _contributors page: https://github.com/pi-top/pitop/graphs/contributors
