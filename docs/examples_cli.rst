=====================================================
Examples - CLI
=====================================================

pt-oled : Redirecting commands to use pi-top [4]'s OLED
--------------------------------------------------------

.. code-block:: bash

    pi@pi-top:~ $ pt-oled "It's $(date '+%A')!"


pt-brightness: Controlling screen brightness
-----------------------------------------------------

.. code-block:: bash

    pi@pi-top:~ $ pt-brightness
    16
    pi@pi-top:~ $ pt-brightness -b 10
    pi@pi-top:~ $ pt-brightness
    10
    pi@pi-top:~ $ pt-brightness -i
    pi@pi-top:~ $ pt-brightness
    11
