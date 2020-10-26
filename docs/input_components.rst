=================================================
API - Input Components
=================================================

These output device component interfaces have been provided for simple use of everyday components, and are intended for general use with the devices they represent.

These components are considered inputs due to their ability to produce a value.


Analogue Components (A Port)
=================================================

PMALightSensor
-------------------------------

.. .. autoclass:: ptpma.PMALightSensor

PMAPotentiometer
-------------------------------

.. .. autoclass:: ptpma.PMAPotentiometer

PMASoundSensor
-------------------------------

.. .. autoclass:: ptpma.PMASoundSensor


Digital Components (D Port)
=================================================

PMAButton
-------------------------------

.. .. autoclass:: ptpma.PMAButton
   :inherited-members: gpiozero.Button
   :exclude-members: pin_factory

PMAUltrasonicSensor
-------------------------------

.. .. autoclass:: ptpma.PMAUltrasonicSensor
    :exclude-members: ECHO_LOCK


USB Components (USB Port)
=================================================

PMACamera
-------------------------------

.. .. autoclass:: ptpma.PMACamera(camera_device_id=0)
    :exclude-members: __init__, from_file_system, from_usb
