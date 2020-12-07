=================================================
API - Input Components
=================================================

These output device component interfaces have been provided for simple use of everyday components, and are intended for general use with the devices they represent.

These components are considered inputs due to their ability to produce a value.


Analogue Components (A Port)
=================================================

LightSensor
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/light_sensor.jpg

.. autoclass:: pitop.pma.LightSensor

Potentiometer
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/potentiometer.jpg

.. autoclass:: pitop.pma.Potentiometer

SoundSensor
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/sound_sensor.jpg

.. autoclass:: pitop.pma.SoundSensor


Digital Components (D Port)
=================================================

Button
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/button.jpg

.. autoclass:: pitop.pma.Button
   :inherited-members: gpiozero.Button
   :exclude-members: pin_factory

UltrasonicSensor
-------------------------------

.. image:: ../_static/pma/foundation_kit/components/ultrasonic_sensor.jpg

.. autoclass:: pitop.pma.UltrasonicSensor
    :exclude-members: ECHO_LOCK
