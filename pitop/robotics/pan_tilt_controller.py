from pitop.pma import ServoMotor


class PanTiltController:

    def __init__(self, pan_servo: ServoMotor, tilt_servo: ServoMotor):
        self._pan_servo = pan_servo
        self._tilt_servo = tilt_servo
