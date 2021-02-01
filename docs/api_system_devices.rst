======================================
API - System Devices
======================================


The pi-top Python SDK provides classes which represent devices, including some that can be used by generic devices, such as USB cameras. These classes are intended to simplify connecting common system devices with pi-top devices.

USB Camera
=====================================

This class provides an easy way to:

* save image and video files
* directly access camera frames
* process frames in the background (via callback)

It is easy to make use of some pre-written video processors, such as motion detection.

It is also possible to make use of this class to read frames from a directory of images,
removing the need for a stream of images from physical hardware. This can be useful for
testing, or simulating a real camera.

.. literalinclude:: ../examples/camera/camera_capture_video.py

By default, camera frames are of :class:`PIL.Image.Image` type (using the Pillow module),
which provides a standardized way of working with the image.
These Image objects use raw, RGB-ordered pixels.

It is also possible to use OpenCV standard format, if desired. This may be useful if you are
intending to do your own image processing with OpenCV. The OpenCV format uses raw, BGR-ordered
pixels in a NumPy :class:`numpy.ndarray` object. This can be done by setting the camera's format
property to "OpenCV":

.. code-block:: python

    from pitop.camera import Camera

    c = Camera()
    c.format = "OpenCV"

This can be also be done by passing the format to the camera's constructor:

.. code-block:: python

    from pitop.camera import Camera

    c = Camera(format="OpenCV")

Using a USB Camera to Access Image Data
---------------------------------------

.. literalinclude:: ../examples/camera/camera_loop_print_first_pixel.py

Using a USB Camera to Capture Video
-----------------------------------

.. literalinclude:: ../examples/camera/camera_capture_video.py

Adding Motion Detection to a USB Camera
---------------------------------------

.. literalinclude:: ../examples/camera/camera_motion_detector.py

Processing Camera Frame
-----------------------

.. literalinclude:: ../examples/camera/camera_image_processing.py

Processing Camera Frame Stream with OpenCV (Convert to grayscale)
-----------------------------------------------------------------

.. literalinclude:: ../examples/camera/camera_image_processing_stream_opencv.py

Class Reference: USB Camera
---------------------------

.. autoclass:: pitop.camera.Camera


Keyboard Button
===============
This class makes it easy to handle a keyboard button in the same way as a
GPIO-based button.

You can listen for any standard keyboard key input. For example, using ``a`` or ``A`` will provide the ability to 'listen' for the A-key being pressed - with or without shift.

.. warning::
   This class depends on pynput, which interfaces with Xorg to handle key press events. This means that this component cannot be used via SSH, or in a headless environment (that is, without a desktop environment).

.. note::
   The DISPLAY environment variable is required to be set in order for this component to work.

.. note::
   If your code is being run from a terminal window, then the key presses will be captured in the terminal output. This can cause confusion and issues around reading output.


.. literalinclude:: ../examples/keyboard/keyboard_button.py

Class Reference: KeyboardButton
--------------------------------------------

.. autoclass:: pitop.keyboard.KeyboardButton


Special Key Names
-----------------

You can listen for the following special keys by passing their names when creating an instance
of KeyboardButton.

==================      ============
Identifier              Description
==================      ============
``alt``                 A generic Alt key. This is a modifier.
``alt_l``               The left Alt key. This is a modifier.
``alt_r``               The right Alt key. This is a modifier.
``alt_gr``              The AltGr key. This is a modifier.
``backspace``           The Backspace key.
``caps_lock``           The CapsLock key.
``cmd``                 A generic command button.
``cmd_l``               The left command button. On PC keyboards, this corresponds to the
                        Super key or Windows key, and on Mac keyboards it corresponds to the Command
                        key. This may be a modifier.
``cmd_r``               The right command button. On PC keyboards, this corresponds to the
                        Super key or Windows key, and on Mac keyboards it corresponds to the Command
                        key. This may be a modifier.
``ctrl``                A generic Ctrl key. This is a modifier.
``ctrl_l``              The left Ctrl key. This is a modifier.
``ctrl_r``              The right Ctrl key. This is a modifier.
``delete``              The Delete key.
``down``                A down arrow key.
``up``                  An up arrow key.
``left``                A left arrow key.
``right``               A right arrow key.
``end``                 The End key.
``enter``               The Enter or Return key.
``esc``                 The Esc key.
``home``                The Home key.
``page_down``           The PageDown key.
``page_up``             The PageUp key.
``shift``               A generic Shift key. This is a modifier.
``shift_l``             The left Shift key. This is a modifier.
``shift_r``             The right Shift key. This is a modifier.
``space``               The Space key.
``tab``                 The Tab key.
``insert``              The Insert key. This may be undefined for some platforms.
``menu``                The Menu key. This may be undefined for some platforms.
``num_lock``            The NumLock key. This may be undefined for some platforms.
``pause``               The Pause/Break key. This may be undefined for some platforms.
``print_screen``        The PrintScreen key. This may be undefined for some platforms.
``scroll_lock``         The ScrollLock key. This may be undefined for some platforms.
``f1``                  The F1 key
``f2``                  The F2 key
``f3``                  The F3 key
``f4``                  The F4 key
``f5``                  The F5 key
``f6``                  The F6 key
``f7``                  The F7 key
``f8``                  The F8 key
``f9``                  The F9 key
``f10``                 The F10 key
``f11``                 The F11 key
``f12``                 The F12 key
``f13``                 The F13 key
``f14``                 The F14 key
``f15``                 The F15 key
``f16``                 The F16 key
``f17``                 The F17 key
``f18``                 The F18 key
``f19``                 The F19 key
``f20``                 The F20 key
==================      ============
