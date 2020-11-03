from pitop.pma.common.servo_motor_registers import (
    ServoControlRegisters,
    ServoRegisterTypes,
    ServoControlModes,
    ServoMotorS1,
    ServoMotorSetup)
from pitop.pma.servo_controller import ServoController, ServoHardwareSpecs, interp, split_into_bytes
from pitop.core.bitwise_ops import join_bytes
from unittest import TestCase
from sys import modules
from unittest.mock import Mock, patch

modules["io"] = Mock()
modules["gpiozero"] = Mock()
modules["gpiozero.exc"] = Mock()
modules["cv2"] = Mock()
modules["numpy"] = Mock()
modules["pitop.core.smbus_device"] = Mock()
modules["pitop.core.logger"] = Mock()
modules["pitop.core.singleton"] = Mock()
modules["pitop.pma.ultrasonic_sensor"] = Mock()


class ServoControllerTestCase(TestCase):

    def test_constructor_success(self):
        controller = ServoController(port="S1")
        self.assertEquals(controller.registers, ServoMotorS1)

    def test_constructor_fails_on_incorrect_port(self):
        """
        Constructor fails if providing an invalid port
        """
        with self.assertRaises(Exception):
            ServoController(port="invalid_port")

    def test_control_mode_read_write(self):
        """
        Registers read/written when setting/reading control modes from MCU
        """
        for servo_port_registers in ServoControlRegisters:
            port_name = servo_port_registers.name
            registers = servo_port_registers.value
            control_mode_register = registers[ServoRegisterTypes.CONTROL_MODE]

            for control_mode in ServoControlModes:
                # create instance
                controller = ServoController(port=port_name)

                # setup r/w mocks
                write_byte_mock = controller._mcu_device.write_byte = Mock()
                read_unsigned_byte_mock = controller._mcu_device.read_unsigned_byte = Mock()
                read_unsigned_byte_mock.return_value = control_mode.value

                # test
                controller.set_control_mode(control_mode)
                write_byte_mock.assert_called_with(control_mode_register, control_mode.value)

                self.assertEquals(controller.control_mode(), control_mode)
                read_unsigned_byte_mock.assert_called_with(control_mode_register)

    def test_set_min_pulse_width_write(self):
        """
        Registers written when setting the minimum pulse width to MCU
        """
        # create instance
        controller = ServoController(port="S1")

        # setup r/w mocks
        write_word_mock = controller._mcu_device.write_word = Mock()

        # test
        min_pulse_width = 500
        controller.set_min_pulse_width(min_pulse_width)
        write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MIN_PULSE_WIDTH, min_pulse_width, signed=False, little_endian=True)

    def test_set_max_pulse_width_write(self):
        """
        Registers written when setting the maximum pulse width to MCU
        """
        # create instance
        controller = ServoController(port="S1")

        # setup r/w mocks
        write_word_mock = controller._mcu_device.write_word = Mock()

        # test
        max_pulse_width = 500
        controller.set_max_pulse_width(max_pulse_width)
        write_word_mock.assert_called_with(ServoMotorSetup.REGISTER_MAX_PULSE_WIDTH, max_pulse_width, signed=False, little_endian=True)

    def test_set_pwm_frequency_read_write(self):
        """
        Registers read/written when setting/reading PWM frequency to/from MCU
        """
        # create instance
        controller = ServoController(port="S1")

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

    def test_control_mode_0_read_write(self):
        """
        Registers read/written when s when using control mode 0 methods
        """
        target_speed = 70
        speed_setting = round(target_speed * 10)

        interp_return_value = 44
        interp.return_value = interp_return_value

        speed_in_bytes = split_into_bytes(interp_return_value, 2, signed=True, little_endian=True) + \
            split_into_bytes(speed_setting, 2, signed=True, little_endian=True)
        speed_read = join_bytes(speed_in_bytes)

        for servo_port_registers in ServoControlRegisters:
            port_name = servo_port_registers.name
            registers = servo_port_registers.value
            speed_register = registers[ServoRegisterTypes.SPEED]

            # create instance
            controller = ServoController(port=port_name)
            controller.control_mode = Mock()
            controller.control_mode.return_value = ServoControlModes.MODE_0

            # setup r/w mocks
            write_word_mock = controller._mcu_device.write_word = Mock()
            read_signed_word_mock = controller._mcu_device.read_signed_word = Mock()
            read_signed_word_mock.return_value = speed_read

            # test
            controller.set_target_speed(target_speed)
            write_word_mock.assert_called_with(speed_register, speed_setting, little_endian=True, signed=True)

            self.assertEquals(controller.get_target_speed(), round(speed_read / 10, 1))
            read_signed_word_mock.assert_called_with(speed_register, little_endian=True)

    def test_control_mode_1_read_write(self):
        """
        Registers read/written when s when using control mode 1 methods
        """
        target_angle = 30
        target_speed = 70

        interp_return_value = 40
        interp.return_value = interp_return_value
        speed_setting = int(round(target_speed * 10))

        angle_and_speed_in_bytes = split_into_bytes(interp_return_value, 2, signed=True, little_endian=True) + \
            split_into_bytes(speed_setting, 2, signed=True, little_endian=True)
        angle_and_speed_read = join_bytes(angle_and_speed_in_bytes)

        for servo_port_registers in ServoControlRegisters:
            port_name = servo_port_registers.name
            registers = servo_port_registers.value
            angle_and_speed_register = registers[ServoRegisterTypes.ANGLE_AND_SPEED]

            # create instance
            controller = ServoController(port=port_name)
            controller.control_mode = Mock()
            controller.control_mode.return_value = ServoControlModes.MODE_1

            # setup r/w mocks
            write_n_bytes_mock = controller._mcu_device.write_n_bytes = Mock()
            read_signed_word_mock = controller._mcu_device.read_signed_word = Mock()
            read_signed_word_mock.return_value = angle_and_speed_read

            # test
            controller.set_target_angle(target_angle, target_speed)
            write_n_bytes_mock.assert_called_with(angle_and_speed_register, angle_and_speed_in_bytes)

            self.assertEquals(controller.get_target_angle(), interp_return_value)
            read_signed_word_mock.assert_called_with(angle_and_speed_register, little_endian=True)

    def test_get_target_speed_returns_none_if_not_on_mode_0(self):
        """
        get_target_speed() returns None if not on Mode 0
        """
        controller = ServoController(port="S1")
        mode_mock = controller.control_mode = Mock()

        mode_mock.return_value = ServoControlModes.MODE_1
        self.assertEquals(controller.get_target_speed(), None)

    def test_get_target_angle_returns_none_if_not_on_mode_1(self):
        """
        get_target_angle() returns None if not on Mode 1
        """
        controller = ServoController(port="S1")
        mode_mock = controller.control_mode = Mock()

        mode_mock.return_value = ServoControlModes.MODE_0
        self.assertEquals(controller.get_target_angle(), None)

    def test_set_target_speed_fails_on_invalid_value(self):
        """
        set_target_speed fails if called with an invalid speed value
        """
        controller = ServoController(port="S1")

        for speed in (-101, -1123, 212, 101):
            with self.assertRaises(ValueError):
                controller.set_target_speed(speed)
