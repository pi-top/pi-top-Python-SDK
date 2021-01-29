======================================
API - Advanced Usage
======================================

PiTop
=====

This class provides a simple abstraction of a pi-top device. It's meant to provide easy access to all the features available in a pi-top, depending on the device that runs the class.

.. literalinclude:: ../examples/system/pitop.py


Class Reference: PiTop
----------------------

.. autoclass:: pitop.PiTop
    :exclude-members: instance
    :members:

AlexRobot
=========

Overview
--------

This class allows you to interact with a pi-top [4] and Robotics Kit, assembled in the
'Alex' configuration.

You can use this class to write code that moves Alex, and interact with the environment
using the camera and ultrasonic sensor.

Note that Alex internally inherits from :class:`pitop.PiTop`; this means that all the features of
that class are available to Alex.

.. literalinclude:: ../examples/robotics/alex.py

AlexRobot class
----------------------

.. autoclass:: pitop.AlexRobot
    :exclude-members: CALIBRATION_FILE_DIR, CALIBRATION_FILE_NAME, instance
    :members:
    :inherited-members:
