======================================
API - System Devices
======================================


The pi-top SDK provides some helpful classes for common system devices:

USB Camera
=====================================

This module provides a Camera class for using a USB Camera attached to your
pi-top. There are methods to: save image and video files; direct access camera
frames in your code; provide a callback to process frames in the background;
and make use of some pre-written video processors such as a motion detection.

The module also provides a mock 'File System Camera' which reads it's frames
from a directory of images for working without camera hardware in situations
such as testing.

.. literalinclude:: ../examples/camera/camera_capture_video.py

By default, Camera frames are provided as instances of the Pillow module
:class:`PIL.Image.Image` class, which provides various methods for working with
the image. These Image objects use raw, RGB-ordered pixels.

The Camera also supports providing frames in the OpenCV standard format. You
can pass the parameter ``format='OpenCV'`` to Camera methods such as
:class:`get_frame` and :class:`start_handling_frames` to have them provide this
format instead. There are also helpers :class:`pil_to_opencv` and
:class:`opencv_to_pil` for performing this conversion yourself. The OpenCV
format uses raw, BGR-ordered pixels in a NumPy :class:`numpy.ndarray` object.

Using a USB Camera to Access Image Data
---------------------------------------

.. literalinclude:: ../examples/camera/camera_loop_print_first_pixel.py

Using a USB Camera to Capture Video
-----------------------------------

.. literalinclude:: ../examples/camera/camera_capture_video.py

Convert USB Camera image to grayscale
-------------------------------------

.. literalinclude:: ../examples/camera/camera_opencv_processing.py

Class Reference: USB Camera
---------------------------

.. autoclass:: pitop.camera.Camera

Keyboard
========

This module has been designed to allow a programmer to utilise keyboard input in the same way as
they might use GPIO input (e.g. a button).

You can listen for any standard keyboard key input, for example by using ``a`` or ``A`` to listen
for the A-key being pressed with or without shift.

.. literalinclude:: ../examples/keyboard/keyboard.py

Class Reference: Keyboard Key Press Listener
--------------------------------------------

.. autoclass:: pitop.keyboard.KeyPressListener


Special Key Names
-----------------

You can listen for the following special keys by passing their names when creating an instance
of KeyPressListener.

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
