from json import load
from pathlib import Path


def __load_json(filename):
    path = __robotics_directory() / "json" / filename
    with open(path, "r") as handle:
        config = load(handle)
    return config


def __robotics_directory() -> Path:
    return Path(__file__).parent


alex_config = __load_json("alex.json")

bobbie_config = __load_json("bobbie.json")


class AlexRobot:
    def __init__(self, *args, **kwargs):
        print(
            "AlexRobot class is deprecated. Please use Pitop.from_config(alex_config)"
        )

    def __new__(cls, *args, **kwargs):
        from pitop.system.pitop import Pitop

        obj = Pitop.from_config(alex_config)
        obj.__class__ = cls
        return obj

    def forward(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.forward(*args, **kwargs)

    def backward(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.backward(*args, **kwargs)

    def left(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.left(*args, **kwargs)

    def right(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.right(*args, **kwargs)

    def rotate(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.rotate(*args, **kwargs)

    def stop_rotation(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.stop_rotation(*args, **kwargs)

    def stop(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.stop(*args, **kwargs)

    def target_lock_drive_angle(self, *args, **kwargs):
        if hasattr(self, "drive"):
            return self.drive.target_lock_drive_angle(*args, **kwargs)

    def calibrate(self, *args, **kwargs):
        if hasattr(self, "pan_tilt"):
            return self.pan_tilt.calibrate(*args, **kwargs)

    @property
    def pan_servo(self):
        if hasattr(self, "pan_tilt"):
            return self.pan_tilt.pan_servo

    @property
    def tilt_servo(self):
        if hasattr(self, "pan_tilt"):
            return self.pan_tilt.tilt_servo
