=====================
API - pi-top Robotics
=====================

.. image:: _static/pma/robotics_kit/Alex.jpg


With the pi-top Robotics and Electronics Kits, you can build different types of robots.
In this SDK, we provide a set of classes that represent some useful configurations.


.. _component-drive-controller:

Drive Controller
=================

.. note::
   This is a composite component that contains two :ref:`EncoderMotor Components<component-encoder-motor>`.

.. literalinclude:: ../examples/recipes/drive_controller.py

.. autoclass:: pitop.robotics.DriveController


.. _component-pan-tilt-controller:

Pan Tilt Controller
===================

.. note::
   This is a composite component that contains two :ref:`ServoMotor Components<component-servo-motor>`.

.. autoclass:: pitop.robotics.PanTiltController


.. _component-pincer-controller:

Pincer Controller
=================

.. note::
   This is a composite component that contains two :ref:`ServoMotor Components<component-servo-motor>`.

.. autoclass:: pitop.robotics.PincerController
