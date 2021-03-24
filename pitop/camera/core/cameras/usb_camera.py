from PIL import Image

from PyV4L2Camera.camera import Camera as V4L2Camera
from PyV4L2Camera.exceptions import CameraError as V4L2CameraError


class UsbCamera:
    def __init__(self, index: int = 0, resolution=None, rotate_angle: int = 0):
        self.index = index
        self.__camera = None

        if rotate_angle not in (-90, 0, 90, 180):
            raise ValueError("Rotate angle must be -90, 0, 90 or 180 degrees")
        else:
            self._rotate_angle = rotate_angle

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
        pil_image = Image.frombytes(
            'RGB',
            (self.__camera.width, self.__camera.height),
            self.__camera.get_frame(),
            'raw',
            'RGB'
        )

        if self._rotate_angle != 0:
            pil_image = pil_image.rotate(angle=self._rotate_angle, expand=True)

        return pil_image
