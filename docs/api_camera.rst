=====================================
API - pi-top Camera Input Component
=====================================

This module provides a Camera class for using a USB Camera attached to your
pi-top. There are methods to: save image and video files; direct access camera
frames in your code; provide a callback to process frames in the background;
and make use of some pre-written video processors such as a motion detection.

The module also provides a mock 'File System Camera' which reads it's frames
from a directory of images for working without camera hardware in situations
such as testing.

.. literalinclude:: ../examples/camera/camera_capture_video.py

Camera frames are instances of the Pillow module
`PIL.Image.Image <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image>`_
class, which provides various methods for working with the image.

For using OpenCV to process the camera frames, the PIL Image can be easily
converted to OpenCV's format using the NumPy module
`asarray <https://numpy.org/doc/stable/reference/generated/numpy.asarray.html>`_
function: ``numpy.asarray(pil_image)``.

.. literalinclude:: ../examples/camera/camera_opencv_processing.py

----------------------
Camera
----------------------

.. autoclass:: pitop.camera.Camera
