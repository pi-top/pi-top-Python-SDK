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

For this to work, please make sure that you include pi-top's apt repository in
your sources. If you're running pi-topOS, this is already done for you. If not,
you can add them by running:

.. code-block:: sh

    $ wget https://apt.pi-top.com/add-sirius
    $ chmod -x ./add-sirius
    $ sudo ./add-sirius


With pi-top's repository added, you can run the following from your pi-top:

.. code-block:: sh

    $ sudo apt update
    $ sudo apt install python3-pitop


Using PyPI
==========

You can also install the latest version of the SDK through PyPI in your pi-top with:

.. code-block:: sh

    $ pip3 install python3-pitop

Note: this will not install the system packages required for all areas of the SDK to work. This may be useful if you wish to use a virtualenv with a different version dependency to the system.

In general, this is not recommended.

Building from source
====================

Building from source is simple:

.. code-block:: sh

    $ git clone https://github.com/pi-top/pi-top-Python-SDK.git
    $ cd pi-top-Python-SDK
    $ pip3 install -e .

Note: this will not install the system packages required for all areas of the SDK to work. This may be useful if you wish to use a virtualenv with a different version dependency to the system.

In general, this is not recommended.

------------------------------------------------
 Checking that the SDK is installed and working
------------------------------------------------

Try and run the following:

.. code-block:: sh

    $ pt-host

If this works, then you should be good to go! Go and check out the Examples section!
