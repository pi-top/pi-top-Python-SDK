=====================================
API - AlexRobot
=====================================

Overview
--------

This class allows you to interact with a pi-top [4] and Robotics Kit, assembled in an
'Alex' configuration.

You can use this class to write code that moves Alex, and interact with the environment
using the camera and ultrasonic sensor.

Note that Alex internally inherits from :class:`pitop.PiTop`; this means that all the features of
that class are avilable to Alex.

To get started, use the example code in your pi-top [4].


Example
--------

.. literalinclude:: ../../examples/robotics/alex.py


AlexRobot class
----------------------

.. autoclass:: pitop.AlexRobot
    :exclude-members: CALIBRATION_FILE_DIR, CALIBRATION_FILE_NAME, instance
    :members:
    :inherited-members:
