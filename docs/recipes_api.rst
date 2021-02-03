=====================================================
Recipes
=====================================================

In addition to the examples provided for each component/device in the API reference section of this documentation, the following recipes demonstrate some of the more advanced capabilities of the pi-top Python SDK. In particular, these recipes focus on practical use-cases that make use of multiple components/devices within the pi-top Python SDK.

Be sure to check out each component/device separately for simple examples of how to use them.

PMA: Using a Button to Control an LED
-------------------------------------

.. literalinclude:: ../examples/recipes/button_led.py

Robotics Kit: DIY Rover
-----------------------

.. literalinclude:: ../examples/recipes/encoder_motor_rover.py

Robotics Kit: Alex Robot - Moving Randomly
------------------------------------------

.. literalinclude:: ../examples/recipes/alex_move_random.py

Robotics Kit: Alex Robot - Line Detection
-----------------------------------------

.. literalinclude:: ../examples/recipes/alex_line_detect.py

Displaying camera stream in pi-top [4]'s miniscreen
---------------------------------------------------

.. literalinclude:: ../examples/recipes/camera_display_in_miniscreen.py

Robotics Kit: Alex Robot - Control using Bluedot
-------------------------------------------------

`BlueDot <https://bluedot.readthedocs.io/en/latest/>`_ is a python library that allows you to control Raspberry Pi projects remotely with a device that runs Android. In this case, we'll use it as a Joystick to control Alex.

Please follow these instructions to setup your pi-top with BlueDot:

1. Download the BlueDot app from the Google Play Store in your Android device.
2. Pair the pi-top [4] with your cellphone. If you don't know how to, please follow `this guide <https://bluedot.readthedocs.io/en/latest/pairpiandroid.html>`_.
3. Install `bluedot` in your pi-top [4]: open a terminal and run `pip3 install bluedot`.
4. Run the example code. It will pause until you complete step 5.
5. Open the BlueDot app in your device and tap `pi-top` from the list of devices.
6. Start moving your robot!

.. literalinclude:: ../examples/recipes/alex_bluedot.py

Using the pi-topPULSE's LED matrix to show the battery level
------------------------------------------------------------

.. literalinclude:: ../examples/recipes/leds-battery.py
