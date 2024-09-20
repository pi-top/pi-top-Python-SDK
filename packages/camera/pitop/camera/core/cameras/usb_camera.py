from os import environ, listdir

from PIL import Image

from pitop.core.ImageFunctions import convert
from pitop.core.import_opencv import import_opencv

valid_rotate_angles = [-270, -180, -90, 0, 90, 180, 270]

# Only show error logs from OpenCV
environ["OPENCV_LOG_LEVEL"] = "ERROR"


class UsbCamera:
    def __init__(
        self,
        index: int = None,
        resolution=None,
        rotate_angle: int = 0,
        flip_top_bottom: bool = False,
        flip_left_right: bool = False,
    ):
        self._camera = None
        if index is None:
            # Allow OpenCV to find the first available camera
            index = -1

        self._flip_top_bottom = flip_top_bottom
        self._flip_left_right = flip_left_right

        if rotate_angle not in valid_rotate_angles:
            raise ValueError(
                f"Rotate angle must be one of "
                f"{', '.join([str(x) for x in valid_rotate_angles[:-1]])} or "
                f"{str(valid_rotate_angles[-1])}"
            )
        else:
            self._rotate_angle = rotate_angle

        def create_camera_object(index, resolution=None):
            cv = import_opencv()
            try:
                # Force V4L2 backend first to avoid warning logs
                cap = cv.VideoCapture(index, cv.CAP_V4L2)
            except Exception:
                cap = None

            # Retry using default backend on failure.
            # Check if device is opened since sometimes VideoCapture
            # doesn't raise an Exception on error
            if cap is None or not cap.isOpened():
                cap = cv.VideoCapture(index)

            if cap is not None and resolution is not None:
                cap.set(3, resolution[0])
                cap.set(4, resolution[1])
            return cap

        self._camera = create_camera_object(index, resolution)
        if self._camera is None and index == -1:
            # If OpenCV fails to find an available camera, try to find one on our own
            for idx in self.list_device_indexes():
                self._camera = create_camera_object(idx, resolution)
                if self._camera:
                    break

        if not self.is_opened():
            self._camera = None
            raise IOError(
                "Error opening camera. Make sure it's correctly connected via USB."
            ) from None

    def __del__(self):
        try:
            if hasattr(self._camera, "release"):
                self._camera.release()
        except AttributeError:
            # Camera was not initialized
            pass

    def get_frame(self):
        if not self.is_opened():
            raise IOError("Camera not connected")

        result, frame = self._camera.read()
        if not result:
            raise ValueError("Couldn't grab frame from camera")

        # Always PIL format
        pil_image = convert(frame, "PIL").rotate(angle=self._rotate_angle, expand=True)

        if self._flip_top_bottom:
            pil_image = pil_image.transpose(method=Image.FLIP_TOP_BOTTOM)

        if self._flip_left_right:
            pil_image = pil_image.transpose(method=Image.FLIP_LEFT_RIGHT)

        return pil_image

    def is_opened(self):
        return self._camera is not None and self._camera.isOpened()

    @staticmethod
    def list_device_indexes():
        VideoCapture = import_opencv().VideoCapture

        # find "video" device indexes in /dev
        device_names = [name for name in listdir("/dev") if "video" in name]
        device_indexes = [int(dev[len("video") :]) for dev in device_names]
        # indexes >= 10 are for bcm2835, not useful for us
        camera_indexes = [i for i in device_indexes if i < 10]
        camera_indexes.sort()

        # Not all devices actually provide video
        # eg: video1 can be a metadata device for video0
        indexes = []
        for index in camera_indexes:
            try:
                cap = VideoCapture(index)
                if cap.read()[0]:
                    indexes.append(index)
                    cap.release()
            except Exception:
                continue

        return indexes
