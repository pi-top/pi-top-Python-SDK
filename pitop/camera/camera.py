from threading import Thread, Event
from inspect import signature

from .core import (
    FrameHandler,
    CameraTypes)
from .core.capture_actions import CaptureActions
from pitop.pma.common import type_check
from .pil_opencv_conversion import pil_to_opencv


class Camera:
    """
    Provides a variety of high-level functionality for using the PMA USB Camera, including capturing
    images and video, and processing image data from the camera

    :type camera_device_id: int
    :param camera_device_id:
        The ID for the port to which this component is connected. Defaults to 0.
    """

    def __init__(self, camera_device_id=0, camera_type=CameraTypes.USB_CAMERA, path_to_images=""):

        if camera_type == CameraTypes.USB_CAMERA:
            from .core import UsbCamera
            self._camera = UsbCamera(camera_device_id)
        elif camera_type == CameraTypes.FILE_SYSTEM_CAMERA:
            from .core import FileSystemCamera
            self._camera = FileSystemCamera(path_to_images)

        self._continue_processing = True
        self._frame_handler = FrameHandler()
        self._new_frame_event = Event()
        self._process_image_thread = Thread(target=self._process_camera_output, daemon=True)
        self._process_image_thread.start()

    @classmethod
    @type_check
    def from_file_system(cls, path_to_images: str):
        """
        Alternative classmethod to create an instance of a :class:`Camera` object using a :data:`FileSystemCamera`
        """
        return cls(camera_type=CameraTypes.FILE_SYSTEM_CAMERA, path_to_images=path_to_images)

    @classmethod
    @type_check
    def from_usb(cls, camera_device_id: int = 0):
        """
        Alternative classmethod to create an instance of a :class:`Camera` object using a :data:`UsbCamera`
        """
        return cls(camera_type=CameraTypes.USB_CAMERA, camera_device_id=camera_device_id)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._camera = None
        self._continue_processing = False
        if self._process_image_thread.is_alive():
            self._process_image_thread.join()

    def is_recording(self):
        """
        Returns True if recording mode is enabled
        """

        return self._frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)

    def is_detecting_motion(self):
        """
        Returns True if motion detection mode is enabled
        """

        return self._frame_handler.is_running_action(CaptureActions.DETECT_MOTION)

    @type_check
    def capture_image(self, output_file_name=""):
        """
        Capture a single frame image to file

        .. note::
            If no :data:`output_file_name` argument is provided, images will be stored in `~/Camera`.

        :type output_file_name: str
        :param output_file_name:
            The filename into which to write the image.
        """

        self._frame_handler.register_action(CaptureActions.CAPTURE_SINGLE_FRAME, locals())

    @type_check
    def start_video_capture(self, output_file_name="", fps=20.0, resolution=None):
        """
        Begin capturing video from the camera.

        .. note::
            If no :data:`output_file_name` argument is provided, video will be stored in `~/Camera`.

        :type output_file_name: str
        :param output_file_name:
            The filename into which to write the video.
        :type fps: int or float
        :param fps:
            The framerate to use for the captured video. Defaults to 20.0 fps
        :type resolution: tuple
        :param resolution:
            The resolution to use for the captured video. Defaults to (640, 368)
        """

        self._frame_handler.register_action(CaptureActions.CAPTURE_VIDEO_TO_FILE, locals())

    def stop_video_capture(self):
        """
        Stop capturing video from the camera. Does nothing unless :class:`start_video_capture` has been called.
        """

        self._frame_handler.remove_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)

    @type_check
    def start_detecting_motion(self, callback_on_motion, moving_object_minimum_area=300):
        """
        Begin processing image data from the camera, attempting to detect motion. When motion is
        detected, call the function passed in.

        .. warning::
            The callback function can take either no arguments or only one, which will be used to provide the image back
            to the user when motion is detected.
            If a callback with another signature is received, the method will raise an exception.

        :type callback_on_motion: function
        :param callback_on_motion:
            A callback function that will be called when motion is detected.
        :type moving_object_minimum_area: int
        :param moving_object_minimum_area:
            The sensitivity of the motion detection, measured as the area of pixels changing between frames that constitutes motion.
        """

        args = locals()
        callback_signature = signature(callback_on_motion)
        if len(callback_signature.parameters) > 1:
            raise ValueError("Invalid callback signature: it should receive at most one argument.")
        self._frame_handler.register_action(CaptureActions.DETECT_MOTION, args)

    def stop_detecting_motion(self):
        """
        Stop running the motion detection processing. Does nothing unless :class:`start_detecting_motion` has been called.
        """

        self._frame_handler.remove_action(CaptureActions.DETECT_MOTION)

    @type_check
    def start_handling_frames(self, callback_on_frame, frame_interval=1, format='PIL'):
        """
        Begin calling the passed callback with each new frame, allowing for custom processing.

        .. warning::
            The callback function can take either no arguments or only one, which will be used to provide the image back
            to the user.
            If a callback with another signature is received, the method will raise an exception.

        :type callback_on_frame: function
        :param callback_on_frame:
            A callback function that will be called every :class:`frame_interval` camera frames.
        :type frame_interval: int
        :param frame_interval:
            The callback will run every frame_interval frames, decreasing the frame rate of processing. Defaults to 1.

        :type format: string
        :param format:
            The image format to provide to the callback. Case-insensitive.
            By default, with format='PIL', the image will be provided as a raw RGB-ordered :class:`PIL.Image.Image` object.
            When ``format='OpenCV'`` the image will be provided as a raw BGR-ordered :class:`numpy.ndarray` as used by OpenCV.
        """

        args = locals()
        callback_signature = signature(callback_on_frame)
        if len(callback_signature.parameters) > 1:
            raise ValueError("Invalid callback signature: it should receive at most one argument.")
        self._frame_handler.register_action(CaptureActions.HANDLE_FRAME, args)

    def stop_handling_frames(self):
        """
        Stops handling camera frames. Does nothing unless :class:`start_handling_frames` has been called.
        """

        self._frame_handler.remove_action(CaptureActions.HANDLE_FRAME)

    def _process_camera_output(self):
        while self._camera and self._continue_processing is True:
            try:
                self._frame_handler.frame = self._camera.get_frame()
                self._new_frame_event.set()
                self._frame_handler.process()
            except Exception as e:
                print(f"There was an error: {e}")

    def current_frame(self, format='PIL'):
        """
        Returns the latest frame captured by the camera. This method is non-blocking and can return the same frame multiple times.

        By default the returned image is formatted as a :class:`PIL.Image.Image`.

        :type format: string
        :param format:
            The image format to return. Case-insensitive.
            By default, with format='PIL', the image will be returned as a raw RGB-ordered :class:`PIL.Image.Image` object.
            When ``format='Opencv'`` the image will be returned as a raw BGR-ordered :class:`numpy.ndarray` as used by OpenCV.
        """
        if format.lower() == 'opencv':
            return pil_to_opencv(self._frame_handler.frame)

        return self._frame_handler.frame

    def get_frame(self, format='PIL'):
        """
        Returns the next frame captured by the camera. This method blocks until a new frame is available.

        :type format: string
        :param format:
            The image format to return. Case-insensitive.
            By default, with format='PIL', the image will be returned as a raw RGB-ordered :class:`PIL.Image.Image` object.
            When ``format='Opencv'`` the image will be returned as a raw BGR-ordered :class:`numpy.ndarray` as used by OpenCV.
        """
        self._new_frame_event.wait()
        self._new_frame_event.clear()

        if format.lower() == 'opencv':
            return pil_to_opencv(self._frame_handler.frame)

        return self._frame_handler.frame
