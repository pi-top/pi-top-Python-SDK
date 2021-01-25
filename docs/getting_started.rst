=================
 Getting Started
=================

--------------------
 Installing the SDK
--------------------

pi-topOS
========

This SDK is pre-installed on pi-topOS, so you don't need to install it manually!

Using apt
=========

The recommended way of getting the latest version is through `apt`.

Check out `Using pi-top Hardware with Raspberry Pi OS`_ in the pi-top knowledge base for how to do this.

.. _Using pi-top Hardware with Raspberry Pi OS: https://knowledgebase.pi-top.com/knowledge/pi-top-and-raspberry-pi-os

Note: if you only want to install the SDK, then you can replace the "Install software packages" step:

.. code-block:: sh

    sudo apt install -y python3-pitop

This will also install additional packages onto your system that the SDK requires in order to work.

Using PyPI
==========

In general, this is not recommended.

You can also install the latest version of the SDK through PyPI in your pi-top with:

.. code-block:: sh

    pip3 install pitop

Note: this will not install the system packages required for all areas of the SDK to work. This may be useful if you wish to use a virtualenv with a different version dependency to the system.

Building from source
====================

In general, this is not recommended.

Building from source is simple:

.. code-block:: sh

    git clone https://github.com/pi-top/pi-top-Python-SDK.git
    cd pi-top-Python-SDK
    pip3 install -e .

Note: this will not install the system packages required for all areas of the SDK to work. This may be useful if you wish to use a virtualenv with a different version dependency to the system.

------------------------------------------------
 Checking that the SDK is installed and working
------------------------------------------------

Try and run the following:

.. code-block:: sh

    pi-top devices hub

If this works, then you should be good to go! Go and check out the Examples section!
