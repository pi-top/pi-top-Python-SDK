=================================================
Installing
=================================================


Using PyPI
=====================

You can install the latest version of the SDK through PyPI into your pi-top with:

.. code-block:: sh

    $ pip3 install py-pitop


Using apt
=====================

The latest version can also be installed through `apt`. In your pi-top, run:

.. code-block:: sh

    $ sudo apt install py-pitop

For this to work, please make sure that you include pi-top's apt repository in
your sources. If you're running pi-topOS they're already configured. If not,
add them by running:

.. code-block:: sh

    $ echo "deb http://apt.pi-top.com/pi-top-os/ sirius main contrib non-free" | sudo tee -a "/etc/apt/sources.list.d/pi-top.list"


Building from Source
=====================

.. code-block:: sh

    $ git clone https://github.com/pi-top/pi-top-Python-SDK.git
    $ cd pi-top-Python-SDK
    $ pip3 install -e .
