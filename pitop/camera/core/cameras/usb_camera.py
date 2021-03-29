from PIL import Image
from os import listdir, system

from PyV4L2Camera.camera import Camera as V4L2Camera
from PyV4L2Camera.exceptions import CameraError as V4L2CameraError
from pitopcommon.command_runner import run_command


class UsbCamera:
    def __init__(self, index=None, resolution=None):
        # if no index is provided, loop over available video devices
        indexes = self.list_device_indexes() if index is None else [index]
        self.__camera = None
        self.index = None

        for idx in indexes:
            try:
                self.__camera = self.create_camera_object(idx, resolution)
                if self.__camera:
                    self.index = idx
                    break
            except V4L2CameraError:
                continue

        if self.__camera is None:
            raise IOError("Error opening camera. Make sure it's correctly connected via USB.") from None

    def create_camera_object(self, index, resolution=None):
        if resolution is not None:
            return V4L2Camera(f"/dev/video{index}", resolution[0], resolution[1])
        else:
            return V4L2Camera(f"/dev/video{index}")

    def __del__(self):
        try:
            if hasattr(self.__camera, "close"):
                self.__camera.close()
        except AttributeError:
            # Camera was not initialized
            pass

    def get_frame(self):
        # Always PIL format
        return Image.frombytes(
            'RGB',
            (self.__camera.width, self.__camera.height),
            self.__camera.get_frame(),
            'raw',
            'RGB'
        )

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
