=====================================
API - pi-top Battery
=====================================

This module provides a simple way to check the current onboard pi-top battery state, and handle
state change events.

This module will work with original pi-top, pi-top [3] and pi-top [4]. pi-topCEED has no onboard battery, and so will not work.

.. literalinclude:: ../examples/battery/battery.py

----------------------
Battery
----------------------

.. autoclass:: pitop.battery.Battery
