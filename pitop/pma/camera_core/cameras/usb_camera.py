from PIL import Image

from PyV4L2Camera.camera import Camera
from PyV4L2Camera.exceptions import CameraError


class UsbCamera:
    def __init__(self, camera_index: int = 0):
        self.camera_id = camera_index
        try:
            self._camera = Camera(f"/dev/video{camera_index}")
        except CameraError:
            raise IOError("Error opening camera. Make sure it's correctly connected via USB.") from None

    def __del__(self):
        if hasattr(self._camera, "close"):
            self._camera.close()

    def get_frame(self):
        return Image.frombytes('RGB',
                               (self._camera.width, self._camera.height),
                               self._camera.get_frame(),
                               'raw',
                               'RGB')
