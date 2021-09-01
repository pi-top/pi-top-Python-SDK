from os import listdir

from PIL import Image

from pitop.core.ImageFunctions import convert
from pitop.core.import_opencv import import_opencv

valid_rotate_angles = [-270, -180, -90, 0, 90, 180, 270]


class UsbCamera:
    def __init__(
        self,
        index: int = None,
        resolution=None,
        rotate_angle: int = 0,
        flip_top_bottom: bool = False,
        flip_left_right: bool = False,
    ):

        VideoCapture = import_opencv().VideoCapture

        self.__camera = None
        self.index = -1 if index is None else index

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
            cap = VideoCapture(index)
            if resolution is not None:
                cap.set(3, resolution[0])
                cap.set(4, resolution[1])
            return cap

        self.__camera = create_camera_object(self.index, resolution)
        if not self.is_opened():
            self.__camera = None
            raise IOError(
                "Error opening camera. Make sure it's correctly connected via USB."
            ) from None

    def __del__(self):
        try:
            if hasattr(self.__camera, "release"):
                self.__camera.release()
        except AttributeError:
            # Camera was not initialized
            pass

    def get_frame(self):
        if not self.is_opened():
            raise IOError("Camera not connected")

        result, frame = self.__camera.read()
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
        return self.__camera is not None and self.__camera.isOpened()

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
