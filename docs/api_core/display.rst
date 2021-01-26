=====================================
API - pi-top Display
=====================================

Overview
--------

This module provides a simple way to check the current onboard pi-top display state, and handle
state change events.

This module will work with original pi-top, pi-topCEED and pi-top [3]. pi-top [4] has no onboard display, and the official pi-top [4] display is not software controllable, and so will not work.

Example
-------

.. literalinclude:: ../../examples/display/display.py

Display
----------------------

.. autoclass:: pitop.display.Display
