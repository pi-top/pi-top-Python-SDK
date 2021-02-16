from pitop import PiTop
from pitop.core.mixins import (
    SupportsCamera,
    SupportsDriving,
    SupportsPanTilt,
)
from pitop.pma import UltrasonicSensor


class AlexRobot(SupportsDriving, SupportsPanTilt, SupportsCamera, PiTop):
    """
    Abstraction of a pi-top [4] and Robotics Kit, assembled in an 'Alex' configuration.

    Inherits from :class:`PiTop`: all methods, attributes and properties from that
    class are also available through an `AlexRobot` object. This class builds on top of
    :class:`PiTop` to make available to the user all the methods to move the robot and
    to interact with all the features available in a pi-top [4].

    :param int camera_device_index: ID of the video capturing device to open. To open the default camera, use 0.
    :param tuple camera_resolution: Tuple with the camera resolution, as (width, height). Defaults to (640, 480).
    :param str ultrasonic_sensor_port: Port where the ultrasonic sensor is connected.
    :param str motor_left_port: Port where the left wheel motor is connected.
    :param str motor_right_port: Port where the right wheel motor is connected.
    :param str servo_pan_port: Port where the servo motor used to pan the camera is connected.
    :param str servo_tilt_port: Port where the servo motor used to tilt the camera is connected.
    """
    def __init__(self,
                 camera_device_index=0,
                 camera_resolution=(640, 480),
                 ultrasonic_sensor_port="D3",
                 motor_left_port="M3",
                 motor_right_port="M0",
                 servo_pan_port="S0",
                 servo_tilt_port="S3",
                 ):
        PiTop.__init__(self)
        SupportsCamera.__init__(self, camera_device_index, camera_resolution)
        SupportsDriving.__init__(self, motor_left_port, motor_right_port)
        SupportsPanTilt.__init__(self, servo_pan_port=servo_pan_port, servo_tilt_port=servo_tilt_port)
        self.ultrasonic_sensor = self.get_or_create_pma_component(UltrasonicSensor, ultrasonic_sensor_port)
