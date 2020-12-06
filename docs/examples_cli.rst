=====================================================
Examples - CLI
=====================================================

Redirecting commands to use pi-top [4]'s OLED
--------------------------------------------------------

.. code-block:: bash

    pi@pi-top:~ $ pi-top oled draw "It's $(date '+%A')!"


Controlling screen brightness
-----------------------------------------------------

.. code-block:: bash

    pi@pi-top:~ $ pi-top display brightness
    16
    pi@pi-top:~ $ pi-top display brightness 10
    pi@pi-top:~ $ pi-top display brightness
    10
    pi@pi-top:~ $ pi-top display brightness -i
    pi@pi-top:~ $ pi-top display brightness
    11
