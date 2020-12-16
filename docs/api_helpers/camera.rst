=====================================
API - USB Camera
=====================================

This module provides a Camera class for using a USB Camera attached to your
pi-top. There are methods to: save image and video files; direct access camera
frames in your code; provide a callback to process frames in the background;
and make use of some pre-written video processors such as a motion detection.

The module also provides a mock 'File System Camera' which reads it's frames
from a directory of images for working without camera hardware in situations
such as testing.

.. literalinclude:: ../../examples/camera/camera_capture_video.py

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
-------------------------------------------------------------------------------

.. literalinclude:: ../../examples/camera/camera_loop_print_first_pixel.py

Using a USB Camera to Capture Video
-------------------------------------------------------------------------------

.. literalinclude:: ../../examples/camera/camera_capture_video.py

Convert USB Camera image to grayscale
-------------------------------------------------------------------------------

.. literalinclude:: ../../examples/camera/camera_opencv_processing.py

----------------------
Camera
----------------------

.. autoclass:: pitop.camera.Camera
.. autofunction:: pitop.camera.pil_to_opencv
.. autofunction:: pitop.camera.opencv_to_pil
