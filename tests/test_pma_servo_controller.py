from sys import modules
from unittest import TestCase
from unittest.mock import Mock, patch


modules_to_patch = [
    "io",
    "gpiozero",
    "gpiozero.exc",
    "cv2",
    "numpy",
    "pitop.common.smbus_device",
    "pitop.common.logger",
    "pitop.common.singleton",
    "pitop.pma.ultrasonic_sensor",
]
for module in modules_to_patch:
    modules[module] = Mock()

from pitop.pma.servo_controller import ServoController
from pitop.pma.common.servo_motor_registers import (
    ServoMotorS0,
    ServoMotorSetup,
    ServoRegisterTypes,
)

# Avoid getting the mocked modules in other tests
for module in modules_to_patch:
    del modules[module]


class ServoControllerTestCase(TestCase):

    def test_constructor_success(self):
        controller = ServoController(port="S0")
        self.assertEquals(controller.registers, ServoMotorS0)

    def test_constructor_fails_on_incorrect_port(self):
        """Constructor fails if providing an invalid port."""
        with self.assertRaises(Exception):
            ServoController(port="invalid_port")

    def test_set_min_pulse_width_write(self):
        """Registers written when setting the minimum pulse width to MCU."""
        # create instance
        controller = ServoController(port="S1")
        # setup mock
        with patch.object(controller._mcu_device, "write_word") as write_word_mock:
            min_pulse_width = 500
            # test
            controller.set_min_pulse_width(min_pulse_width)
            write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MIN_PULSE_WIDTH, min_pulse_width, signed=False, little_endian=True)

    def test_set_max_pulse_width_write(self):
        """Registers written when setting the maximum pulse width to MCU."""
        # create instance
        controller = ServoController(port="S1")
        # setup mock
        with patch.object(controller._mcu_device, "write_word") as write_word_mock:
            max_pulse_width = 500
            # test
            controller.set_max_pulse_width(max_pulse_width)
            write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MAX_PULSE_WIDTH, max_pulse_width, signed=False, little_endian=True)

    def test_set_pwm_frequency_read_write(self):
        """Registers read/written when setting/reading PWM frequency to/from
        MCU."""
        # create instance
        controller = ServoController(port="S0")

        pwm_frequency_value = 200
        with patch.object(controller, "_mcu_device") as mcu_device_mock:
            # setup r/w mocks
            write_byte_mock = mcu_device_mock.write_byte = Mock()
            read_unsigned_byte_mock = mcu_device_mock.read_unsigned_byte = Mock(return_value=pwm_frequency_value)

            # test
            controller.set_pwm_frequency(pwm_frequency_value)
            write_byte_mock.assert_called_with(ServoMotorSetup.REGISTER_PWM_FREQUENCY, pwm_frequency_value)

            self.assertEquals(controller.pwm_frequency(), pwm_frequency_value)
            read_unsigned_byte_mock.assert_called_with(ServoMotorSetup.REGISTER_PWM_FREQUENCY)

    def test_acceleration_mode_read_write(self):
        """Registers read/written when setting/reading acceleration mode
        to/from MCU."""
        # create instance
        controller = ServoController(port="S0")

        with patch.object(controller, "_mcu_device") as mcu_device_mock:
            for acceleration_mode in (0, 1):
                # setup r/w mocks
                write_byte_mock = mcu_device_mock.write_byte = Mock()
                read_unsigned_byte_mock = mcu_device_mock.read_unsigned_byte = Mock(return_value=acceleration_mode)

                # test
                controller.set_acceleration_mode(acceleration_mode)
                write_byte_mock.assert_called_with(ServoMotorS0.get(ServoRegisterTypes.ACC_MODE), acceleration_mode)

                self.assertEquals(controller.get_acceleration_mode(), acceleration_mode)
                read_unsigned_byte_mock.assert_called_with(ServoMotorS0.get(ServoRegisterTypes.ACC_MODE))

    def test_acceleration_mode_fails_on_invalid_type(self):
        """Can't set acceleration mode if provided mode has invalid type."""
        controller = ServoController(port="S0")

        for acceleration_mode in ('a', 0.1):
            with self.assertRaises(TypeError):
                controller.set_acceleration_mode(acceleration_mode)
