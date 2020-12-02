from enum import Enum

from .usb_camera import UsbCamera
from .file_system_camera import FileSystemCamera


class CameraTypes(Enum):
    USB_CAMERA = UsbCamera
    FILE_SYSTEM_CAMERA = FileSystemCamera
