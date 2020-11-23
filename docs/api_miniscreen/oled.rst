===================================
API - pi-top [4] Mini Screen - OLED
===================================

This module contains information to allow a programmer to work with the mini-screen on the pi-top [4].
Below you will find a list of the different objects that can be created to do this along with their
descriptions, methods and examples of how to do this.

To get started you can copy and paste some of the examples into your own program to try them out. The
**OLEDDisplay** class has some simple methods to interact with the screen, allowing you to draw text and
simple images. For displaying more advanced things, you may need to investigate the **Canvas** class.
Finally, you may find the **OLEDImage** class useful if you'd like to display animated images on the screen.

**Note:** When you create a `OLEDDisplay` object in your program, the mini-screen on the pi-top [4] will
clear and is then controlled by your code. You will not be able to access the system menu on the mini-screen
until your program exits, at which point the system menu is automatically restored. If you need to provide
yourself with a method of being able to exit, it is recommended that you check for a press event on the
'cancel' button:

.. literalinclude:: ../../examples/miniscreen/exit_with_cancel_button.py

Whilst this snippet is provided for ease of use, it is strongly recommended that you look at the documentation for the pi-top [4] buttons for detailed instructions of its usage.

---------------------
OLEDDisplay class
---------------------

.. automodule:: pitop.miniscreen.oled
    :members:
    :undoc-members:
    :show-inheritance:

---------------------
Canvas class
---------------------

.. automodule:: pitop.miniscreen.oled.canvas
    :members:
    :undoc-members:
    :show-inheritance:

---------------------
OLEDImage class
---------------------

.. automodule:: pitop.miniscreen.oled.oled_image
    :members:
    :undoc-members:
    :show-inheritance:
