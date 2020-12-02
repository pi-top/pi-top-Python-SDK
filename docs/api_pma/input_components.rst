=================================================
API - Input Components
=================================================

These output device component interfaces have been provided for simple use of everyday components, and are intended for general use with the devices they represent.

These components are considered inputs due to their ability to produce a value.


Analogue Components (A Port)
=================================================

LightSensor
-------------------------------

.. autoclass:: pitop.pma.LightSensor

Potentiometer
-------------------------------

.. autoclass:: pitop.pma.Potentiometer

SoundSensor
-------------------------------

.. autoclass:: pitop.pma.SoundSensor


Digital Components (D Port)
=================================================

Button
-------------------------------

.. autoclass:: pitop.pma.Button
   :inherited-members: gpiozero.Button
   :exclude-members: pin_factory

UltrasonicSensor
-------------------------------

.. autoclass:: pitop.pma.UltrasonicSensor
    :exclude-members: ECHO_LOCK
