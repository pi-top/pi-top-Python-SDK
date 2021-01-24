from PIL import Image

from PyV4L2Camera.camera import Camera as V4L2Camera
from PyV4L2Camera.exceptions import CameraError as V4L2CameraError


class UsbCamera:
    def __init__(self, index: int = 0, resolution=None):
        self.index = index

        try:
            if resolution is not None:
                self.__camera = V4L2Camera(f"/dev/video{index}", resolution[0], resolution[1])
            else:
                self.__camera = V4L2Camera(f"/dev/video{index}")

        except V4L2CameraError:
            raise IOError(f"Error opening camera {index}. Make sure it's correctly connected via USB.") from None

    def __del__(self):
        if hasattr(self.__camera, "close"):
            self.__camera.close()

    def get_frame(self):
        # Always PIL format
        return Image.frombytes(
            'RGB',
            (self.__camera.width, self.__camera.height),
            self.__camera.get_frame(),
            'raw',
            'RGB'
        )
