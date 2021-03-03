from unittest.mock import Mock
from sys import modules

modules["io"] = Mock()
modules["gpiozero"] = Mock()
modules["gpiozero.exc"] = Mock()
modules["cv2"] = Mock()
modules["numpy"] = Mock()
modules["pitopcommon.smbus_device"] = Mock()
modules["pitopcommon.logger"] = Mock()
modules["pitopcommon.singleton"] = Mock()
modules["pitop.pma.ultrasonic_sensor"] = Mock()

from pitop.pma.servo_controller import ServoController
from pitop.pma.common.servo_motor_registers import (
    ServoMotorS0,
    ServoMotorSetup
)
from unittest import TestCase, skip


@skip
class ServoControllerTestCase(TestCase):

    def test_constructor_success(self):
        controller = ServoController(port="S1")
        self.assertEquals(controller.registers, ServoMotorS0)

    def test_constructor_fails_on_incorrect_port(self):
        """Constructor fails if providing an invalid port."""
        with self.assertRaises(Exception):
            ServoController(port="invalid_port")

    def test_set_min_pulse_width_write(self):
        """Registers written when setting the minimum pulse width to MCU."""
        # create instance
        controller = ServoController(port="S1")

        # setup r/w mocks
        write_word_mock = controller._mcu_device.write_word = Mock()

        # test
        min_pulse_width = 500
        controller.set_min_pulse_width(min_pulse_width)
        write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MIN_PULSE_WIDTH, min_pulse_width, signed=False, little_endian=True)

    def test_set_max_pulse_width_write(self):
        """Registers written when setting the maximum pulse width to MCU."""
        # create instance
        controller = ServoController(port="S1")

        # setup r/w mocks
        write_word_mock = controller._mcu_device.write_word = Mock()

        # test
        max_pulse_width = 500
        controller.set_max_pulse_width(max_pulse_width)
        write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MAX_PULSE_WIDTH, max_pulse_width, signed=False, little_endian=True)

    def test_set_pwm_frequency_read_write(self):
        """Registers read/written when setting/reading PWM frequency to/from
        MCU."""
        # create instance
        controller = ServoController(port="S0")

        # setup r/w mocks
        pwm_frequency_value = 200
        write_byte_mock = controller._mcu_device.write_byte = Mock()
        read_unsigned_byte_mock = controller._mcu_device.read_unsigned_byte = Mock()
        read_unsigned_byte_mock.return_value = pwm_frequency_value

        # test
        controller.set_pwm_frequency(pwm_frequency_value)
        write_byte_mock.assert_called_with(ServoMotorSetup.REGISTER_PWM_FREQUENCY, pwm_frequency_value)

        self.assertEquals(controller.pwm_frequency(), pwm_frequency_value)
        read_unsigned_byte_mock.assert_called_with(ServoMotorSetup.REGISTER_PWM_FREQUENCY)

    def test_set_target_speed_fails_on_invalid_value(self):
        """set_target_speed fails if called with an invalid speed value."""
        controller = ServoController(port="S1")

        for speed in (-101, -1123, 212, 101):
            with self.assertRaises(ValueError):
                controller.set_target_speed(speed)
