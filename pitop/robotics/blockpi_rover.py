from pitop.robotics.drive_controller import DriveController
from pitop.system.pitop import Pitop


class BlockPiRover(Pitop):
    """A rover class for use with BlockPi coding in Further, with a simplified
    API.

    Inherits from Pitop. Constructor adds a DriveController to simplify
    use. DriveController methods are made available on the instance.
    """

    def __init__(self, left_motor="M3", right_motor="M0"):
        Pitop.__init__(self)

        drive = DriveController(
            left_motor_port=left_motor, right_motor_port=right_motor
        )
        self.add_component(drive)

    def forward(self, *args, **kwargs):
        self.drive.forward(*args, **kwargs)

    def backward(self, *args, **kwargs):
        self.drive.backward(*args, **kwargs)

    def left(self, *args, **kwargs):
        self.drive.left(*args, **kwargs)

    def right(self, *args, **kwargs):
        self.drive.right(*args, **kwargs)

    def stop(self, *args, **kwargs):
        self.drive.stop(*args, **kwargs)

    def move(self, *args, **kwargs):
        self.drive.robot_move(*args, **kwargs)
