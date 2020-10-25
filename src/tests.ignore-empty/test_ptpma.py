from unittest.mock import MagicMock, patch
from unittest import TestCase, main
from sys import modules


modules["gpiozero"] = MagicMock()
modules["gpiozero.exc"] = MagicMock()
modules["smbus2"] = MagicMock()
modules["ptcommon.i2c_device"] = MagicMock()
modules["ptcommon.smbus_device"] = MagicMock()
modules["ptcommon.logger"] = MagicMock()
modules["ptcommon.singleton"] = MagicMock()
modules["ptcommon.bitwise_ops"] = MagicMock()
modules["cv2"] = MagicMock()
modules["numpy"] = MagicMock()


from ptpma import (
    PMAButton,
    PMABuzzer,
    PMACamera,
    PMAInertialMeasurementUnit,
    PMALed,
    PMALightSensor,
    PMAPotentiometer,
    PMASoundSensor,
    PMAUltrasonicSensor,
    PMAEncoderMotor,
    PMAServoMotor
)  # noqa: E402


class PMATestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


if __name__ == "__main__":
    main()
