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

Robotics Kit: Robot - Moving Randomly
------------------------------------------

.. literalinclude:: ../examples/recipes/robot_move_random.py

Robotics Kit: Robot - Line Detection
-----------------------------------------

.. literalinclude:: ../examples/recipes/robot_line_detect.py

Displaying camera stream in pi-top [4]'s miniscreen
---------------------------------------------------

.. literalinclude:: ../examples/recipes/camera_display_in_miniscreen.py

Robotics Kit: Robot - Control using Bluedot
-------------------------------------------------

.. note::

   `BlueDot <https://bluedot.readthedocs.io/en/latest/>`_ is a Python library that allows you to control Raspberry Pi projects remotely. This example demonstrates a way to control a robot with a virtual joystick.

.. literalinclude:: ../examples/recipes/robot_bluedot.py

Using the pi-topPULSE's LED matrix to show the battery level
------------------------------------------------------------

.. literalinclude:: ../examples/recipes/leds-battery.py

Choose a pi-top [4] miniscreen startup animation
------------------------------------------------

.. note::

   This code makes use of the `GIPHY SDK <https://developers.giphy.com/>`_. Follow the instructions `here <https://developers.giphy.com/docs/api>`_ to find out how to apply for an API Key to use with this project.

   Replace `<MY GIPHY KEY>` with the key provided (keep the quotes).

   You can change the type of images that you get by changing `SEARCH_TERM = "Monochrome"` to whatever you want.

.. literalinclude:: ../examples/recipes/giphy_miniscreen_startup.py
