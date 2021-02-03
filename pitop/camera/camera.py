from .core import UsbCamera
from .core import FileSystemCamera
from .core import (
    FrameHandler,
    CameraTypes)
from .core.capture_actions import CaptureActions
from pitop.core import ImageFunctions

from pitop.pma.common import type_check

from threading import Thread, Event
from inspect import signature


class Camera:
    """
    Provides a variety of high-level functionality for using the PMA USB Camera, including capturing
    images and video, and processing image data from the camera

    :type index: int
    :param index:
        ID of the video capturing device to open.
        To open default camera using default backend just pass 0.
    """
    __VALID_FORMATS = ('opencv', 'pil')

    def __init__(self,
                 index=0,
                 resolution=None,
                 camera_type=CameraTypes.USB_CAMERA,
                 path_to_images="",
                 format='PIL'
                 ):

        # Initialise private variables
        self._resolution = resolution
        self._format = None

        # Set format using setter property function
        self.format = format

        # Frame callback
        self.on_frame = None

        # Internal
        self._index = index
        self._camera_type = camera_type
        self._path_to_images = path_to_images

        if self._camera_type == CameraTypes.USB_CAMERA:
            self.__camera = UsbCamera(self._index, self._resolution)

        elif self._camera_type == CameraTypes.FILE_SYSTEM_CAMERA:
            self.__camera = FileSystemCamera(self._path_to_images)

        self.__continue_processing = True
        self.__frame_handler = FrameHandler()
        self.__new_frame_event = Event()
        self.__process_image_thread = Thread(target=self.__process_camera_output, daemon=True)
        self.__process_image_thread.start()

    @classmethod
    @type_check
    def from_file_system(cls, path_to_images: str):
        """
        Alternative classmethod to create an instance of a :class:`Camera` object using a :data:`FileSystemCamera`
        """
        return cls(camera_type=CameraTypes.FILE_SYSTEM_CAMERA, path_to_images=path_to_images)

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, format_value):
        ImageFunctions.image_format_check(format_value)
        self._format = format_value.lower()

    @classmethod
    @type_check
    def from_usb(cls, index: int = 0):
        """
        Alternative classmethod to create an instance of a :class:`Camera` object using a :data:`UsbCamera`
        """
        return cls(camera_type=CameraTypes.USB_CAMERA, index=index)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__camera = None
        self.__continue_processing = False
        if self.__process_image_thread.is_alive():
            self.__process_image_thread.join()

    def is_recording(self):
        """
        Returns True if recording mode is enabled
        """

        return self.__frame_handler.is_running_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)

    def is_detecting_motion(self):
        """
        Returns True if motion detection mode is enabled
        """

        return self.__frame_handler.is_running_action(CaptureActions.DETECT_MOTION)

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

        self.__frame_handler.register_action(CaptureActions.CAPTURE_SINGLE_FRAME, locals())

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

        self.__frame_handler.register_action(CaptureActions.CAPTURE_VIDEO_TO_FILE, locals())

    def stop_video_capture(self):
        """
        Stop capturing video from the camera. Does nothing unless :class:`start_video_capture` has been called.
        """

        self.__frame_handler.remove_action(CaptureActions.CAPTURE_VIDEO_TO_FILE)

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
        self.__frame_handler.register_action(CaptureActions.DETECT_MOTION, args)

    def stop_detecting_motion(self):
        """
        Stop running the motion detection processing. Does nothing unless :class:`start_detecting_motion` has been called.
        """

        self.__frame_handler.remove_action(CaptureActions.DETECT_MOTION)

    @type_check
    def start_handling_frames(self, callback_on_frame, frame_interval=1, format=None):
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
            DEPRECATED. Set 'camera.format' directly, and call this function directly instead.
        """
        if format is not None:
            print("'format' is no longer supported in this function. "
                  "Please set the 'camera.format' property directly, and call this function without 'format' parameter.")

        args = locals()
        args.update({'format': self.format})
        callback_signature = signature(callback_on_frame)
        if len(callback_signature.parameters) == 0:
            raise ValueError("Invalid callback signature: it should receive at least one argument.")
        self.__frame_handler.register_action(CaptureActions.HANDLE_FRAME, args)

    def stop_handling_frames(self):
        """
        Stops handling camera frames. Does nothing unless :class:`start_handling_frames` has been called.
        """

        self.__frame_handler.remove_action(CaptureActions.HANDLE_FRAME)

    def __get_processed_current_frame(self):
        image = self.__frame_handler.frame

        if self.format.lower() == "opencv":
            image = ImageFunctions.convert(image, format="opencv")

        return image

    def __process_camera_output(self):
        while self.__camera and self.__continue_processing is True:
            self.__frame_handler.frame = self.__camera.get_frame()
            self.__new_frame_event.set()

            if callable(self.on_frame):
                self.on_frame(self.__get_processed_current_frame())

            try:
                self.__frame_handler.process()
            except Exception as e:
                print(f"Error in camera frame handler: {e}")

    def current_frame(self, format=None):
        """
        Returns the latest frame captured by the camera. This method is non-blocking and can return the same frame multiple times.

        By default the returned image is formatted as a :class:`PIL.Image.Image`.

        :type format: string
        :param format:
            DEPRECATED. Set 'camera.format' directly, and call this function directly instead.
        """
        if format is not None:
            print("'format' is no longer supported in this function. "
                  "Please set the 'camera.format' property directly, and call this function without 'format' parameter.")

        return self.__get_processed_current_frame()

    def get_frame(self, format=None):
        """
        Returns the next frame captured by the camera. This method blocks until a new frame is available.

        :type format: string
        :param format:
            DEPRECATED. Set 'camera.format' directly, and call this function directly instead.
        """
        if format is not None:
            print("'format' is no longer supported in this function. "
                  "Please set the 'camera.format' property directly, and call this function without 'format' parameter.")

        self.__new_frame_event.wait()
        self.__new_frame_event.clear()

        return self.__get_processed_current_frame()
