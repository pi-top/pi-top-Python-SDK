============================
API - pi-top [4] OLED Screen
============================

This module contains information to allow a programmer to work with the mini-screen on the pi-top [4].
Below you will find a list of the different objects that can be created to do this along with their
descriptions, methods and examples of how to do this.

To get started you can copy and paste some of the examples into your own program to try them out. The
**PTOLEDDisplay** class has some simple methods to interact with the screen, allowing you to draw text and
simple images. For displaying more advanced things, you may need to investigate the **Canvas** class.
Finally, you may find the **OLEDImage** class useful if you'd like to display animated images on the screen.

**Note:** When you create a `PTOLEDDisplay` object in your program, the mini-screen on the pi-top [4] will
clear and is then controlled by your code. You will not be able to access the system menu on the mini-screen
until your program exits, at which point the system menu is automatically restored. If you need to provide
yourself with a method of being able to exit, it is recommended that you check for a press event on the
'cancel' button:

.. literalinclude:: ../../examples/oled/exit_with_cancel_button.py

Whilst this snippet is provided for ease of use, it is strongly recommended that you look at the documentation for the pi-top [4] buttons for detailed instructions of its usage.


PTOLEDDisplay class
---------------------

**Example 1:** Hello, world!

.. literalinclude:: ../../examples/oled/hello_world.py

**Example 2:** Displaying an image

.. literalinclude:: ../../examples/oled/display_an_image.py

**Example 3:** Displaying an animated image once

.. literalinclude:: ../../examples/oled/animated_image_once_simple_way.py

**Example 4:** Displaying an animated image once through frame by frame

.. literalinclude:: ../../examples/oled/animated_image_once.py

**Example 5:** Displaying an animated image looping forever frame by frame

.. literalinclude:: ../../examples/oled/animated_image_loop.py

**Example 6:** Displaying an animated image looping in background

.. literalinclude:: ../../examples/oled/animated_image_loop_in_background.py

.. automodule:: pitop.oled
    :members:
    :undoc-members:
    :show-inheritance:

Canvas class
---------------------

**Example 1:** Drawing with the canvas

.. literalinclude:: ../../examples/oled/drawing_with_canvas.py

**Example 2:** Drawing a clock

.. literalinclude:: ../../examples/oled/clock.py

**Example 3:** A particle-based screensaver

.. literalinclude:: ../../examples/oled/particles.py

**Example 4:** Prim's algorithm

.. literalinclude:: ../../examples/oled/prims_algorithm.py


.. automodule:: pitop.oled.canvas
    :members:
    :undoc-members:
    :show-inheritance:

OLEDImage class
---------------------

.. automodule:: pitop.oled.oled_image
    :members:
    :undoc-members:
    :show-inheritance:
