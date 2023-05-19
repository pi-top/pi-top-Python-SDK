__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# import early incase env PITOP_VIRTUAL_HARDWARE indicates to apply mocks
import pitop.simulation

# System Devices
from pitop.battery import Battery
from pitop.camera import Camera
from pitop.display import Display
from pitop.keyboard import KeyboardButton
from pitop.miniscreen import Miniscreen

# PMA
from pitop.pma import (
    IMU,
    LED,
    Button,
    Buzzer,
    EncoderMotor,
    LightSensor,
    Potentiometer,
    ServoMotor,
)
from pitop.pma import ServoMotorSetting
from pitop.pma import ServoMotorSetting as ServoMotorState
from pitop.pma import SoundSensor, UltrasonicSensor
from pitop.pma.parameters import BrakingType, Direction, ForwardDirection

# Robotics
from pitop.robotics.blockpi_rover import BlockPiRover
from pitop.robotics.configurations import AlexRobot  # deprecated
from pitop.robotics.configurations import alex_config
from pitop.robotics.drive_controller import DriveController
from pitop.robotics.navigation import NavigationController
from pitop.robotics.pan_tilt_controller import PanTiltController
from pitop.robotics.pincer_controller import PincerController
from pitop.robotics.tilt_roll_head_controller import TiltRollHeadController

# Top-level
from pitop.system.pitop import Pitop
from pitop.version import __version__
