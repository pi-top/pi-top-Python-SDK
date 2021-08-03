from PIL import Image
from os import listdir, system

from PyV4L2Camera.camera import Camera as V4L2Camera
from PyV4L2Camera.exceptions import CameraError as V4L2CameraError
from pitop.common.command_runner import run_command


valid_rotate_angles = [-270, -180, -90, 0, 90, 180, 270]


class UsbCamera:
    def __init__(self,
                 index: int = None,
                 resolution=None,
                 rotate_angle: int = 0,
                 flip_top_bottom: bool = False,
                 flip_left_right: bool = False):

        # if no index is provided, loop over available video devices
        indexes = self.list_device_indexes() if index is None else [index]
        self.__camera = None
        self.index = None

        self._flip_top_bottom = flip_top_bottom
        self._flip_left_right = flip_left_right

        if rotate_angle not in valid_rotate_angles:
            raise ValueError(f"Rotate angle must be one of "
                             f"{', '.join([str(x) for x in valid_rotate_angles[:-1]])} or "
                             f"{str(valid_rotate_angles[-1])}")
        else:
            self._rotate_angle = rotate_angle

        def create_camera_object(index, resolution=None):
            if resolution is not None:
                return V4L2Camera(f"/dev/video{index}", resolution[0], resolution[1])
            else:
                return V4L2Camera(f"/dev/video{index}")

        for idx in indexes:
            try:
                self.__camera = create_camera_object(idx, resolution)
                if self.__camera:
                    self.index = idx
                    break
            except V4L2CameraError:
                continue

        if self.__camera is None:
            raise IOError("Error opening camera. Make sure it's correctly connected via USB.") from None

    def __del__(self):
        try:
            if hasattr(self.__camera, "close"):
                self.__camera.close()
        except AttributeError:
            # Camera was not initialized
            pass

    def get_frame(self):
        # Always PIL format
        pil_image = Image.frombytes(
            'RGB',
            (self.__camera.width, self.__camera.height),
            self.__camera.get_frame(),
            'raw',
            'RGB'
        ).rotate(angle=self._rotate_angle, expand=True)

        if self._flip_top_bottom:
            pil_image = pil_image.transpose(method=Image.FLIP_TOP_BOTTOM)

        if self._flip_left_right:
            pil_image = pil_image.transpose(method=Image.FLIP_LEFT_RIGHT)

        return pil_image

    @staticmethod
    def list_device_indexes():
        try:
            run_command("dpkg -l v4l-utils", timeout=1, log_errors=False)
        except Exception:
            print("Warning: can't autodetect camera device indexes, using default value 0.")
            print("Warning: Package v4l-utils is not installed. You can install it by running 'sudo apt install v4l-utils'.")
            return [0]

        indexes = []
        device_names = [name for name in listdir("/dev") if "video" in name]

        # Not all devices actually provide video
        # eg: video1 can be a metadata device for video0
        for device in device_names:
            cmd = f"v4l2-ctl --list-formats --device /dev/{device} | grep -qE '[[0-9]]'"
            try:
                if system(cmd) != 0:
                    continue
                index = int(device[len("video"):])
                # indexes > 10 are for bcm2835, not useful for us
                if index < 10:
                    indexes.append(index)
            except Exception:
                continue

        indexes.sort()
        return indexes
