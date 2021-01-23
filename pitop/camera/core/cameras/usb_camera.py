from PIL import Image

from PyV4L2Camera.camera import Camera
from PyV4L2Camera.exceptions import CameraError


class UsbCamera:
    def __init__(self, camera_index: int = 0):
        self.camera_id = camera_index
        try:
            self.__camera = Camera(f"/dev/video{camera_index}")
        except CameraError:
            raise IOError(f"Error opening camera {camera_index}. Make sure it's correctly connected via USB.") from None

    def __del__(self):
        if hasattr(self.__camera, "close"):
            self.__camera.close()

    def get_frame(self):
        return Image.frombytes('RGB',
                               (self.__camera.width, self.__camera.height),
                               self.__camera.get_frame(),
                               'raw',
                               'RGB')
