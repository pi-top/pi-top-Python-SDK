===============================
API - pi-top Peripheral Devices
===============================

pi-topPROTO+
==================

This module provides a simple way to use a pi-topPROTO+'s onboard ADC (analog-to-digital converter), and make use of it as a distance sensor.

This module will work with original pi-top, pi-topCEED and pi-top [3]. pi-top [4] does not support the modular rail connector, and so will not work.

Using the pi-topPROTO+ as a Distance Sensor
-------------------------------------------

.. literalinclude:: ../examples/protoplus/distance_sensor.py

Class Reference: pi-topPROTO+ Distance Sensor
---------------------------------------------

.. autoclass:: pitop.protoplus.sensors.DistanceSensor


Using the pi-topPROTO+'s onboard ADC
------------------------------------

.. literalinclude:: ../examples/protoplus/adc.py

Class Reference: pi-topPROTO+ ADC Probe
---------------------------------------

.. autoclass:: pitop.protoplus.adc.ADCProbe

pi-topPULSE
===========

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

Using the pi-topPULSE's LED matrix: Test colors
-----------------------------------------------

.. literalinclude:: ../examples/pulse/leds-test_colors.py

Using the pi-topPULSE's LED matrix: Fancy Light Show!
-----------------------------------------------------

.. literalinclude:: ../examples/pulse/leds-fancy_demo.py

Using the pi-topPULSE's LED matrix: Showing CPU temperature
-----------------------------------------------------------

.. literalinclude:: ../examples/pulse/leds-cpu_temp.py

Using the pi-topPULSE's LED matrix: Showing CPU usage
-----------------------------------------------------

.. literalinclude:: ../examples/pulse/leds-cpu_usage.py

Module Reference: pi-topPULSE Configuration
-------------------------------------------

.. automodule:: pitop.pulse.configuration
    :members:
    :undoc-members:
    :show-inheritance:

Module Reference: pi-topPULSE LED Matrix
----------------------------------------

.. automodule:: pitop.pulse.ledmatrix
    :members:
    :undoc-members:
    :show-inheritance:

Module Reference: pi-topPULSE Microphone
----------------------------------------

.. automodule:: pitop.pulse.microphone
    :members:
    :undoc-members:
    :show-inheritance:
