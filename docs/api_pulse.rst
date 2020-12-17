======================================================
API - pi-topPULSE
======================================================

.. image:: _static/peripherals/pi-topPULSE.jpg

This module provides a simple way to use a pi-topPULSE.

This module will work with any Raspberry Pi and/or pi-top.

The hardware representation of each color is 5 bits e.g. only 32 different values.
Without gamma correction, this would mean the actual color value
changes only every 8th color intensity value.
This module applies gamma correction, which means that pixels with seemingly
different intensities actually have the same.

Advanced: EEPROM
----------------
The pi-topPULSE contains an EEPROM which was programmed using `this settings file`_.
during factory production.

.. _this settings file: ./_static/pulse_eeprom_settings.txt

See the Raspberry Pi Foundation's `HAT Github
repository <https://github.com/raspberrypi/hats>`__ for more information.


Using the pi-topPULSE's microphone
----------------------------------
.. literalinclude:: ../examples/pulse/mic-demo.py

Using the pi-topPULSE's LEDs
----------------------------------
.. literalinclude:: ../examples/pulse/leds-test_colors.py

----------------------
pi-topPULSE
----------------------

.. automodule:: pitop.pulse.configuration
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: pitop.pulse.ledmatrix
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: pitop.pulse.microphone
    :members:
    :undoc-members:
    :show-inheritance:
