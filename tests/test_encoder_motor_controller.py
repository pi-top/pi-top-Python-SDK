from pitop.pma.parameters import BrakingType
from pitop.pma.common.encoder_motor_registers import (
    MotorControlRegisters,
    MotorRegisterTypes,
    MotorControlModes,
    EncoderMotorM1)
from pitop.pma.encoder_motor import EncoderMotor
from pitop.pma.encoder_motor_controller import (
    EncoderMotorController, PlateInterface, split_into_bytes)
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


class EncoderMotorControllerTestCase(TestCase):

    @patch.object(EncoderMotorController, "set_braking_type")
    def test_constructor_success(self, set_braking_type_mock):
        braking_type = 1

        controller = EncoderMotorController(
            port="M1",
            braking_type=braking_type)

        self.assertEquals(controller.registers, EncoderMotorM1)
        self.assertEquals(controller._MAX_DC_MOTOR_RPM, 6000)
        set_braking_type_mock.assert_called_once_with(braking_type)

    def test_constructor_fails_on_incorrect_port(self):
        """
        Constructor fails if providing an invalid port
        """
        with self.assertRaises(Exception):
            EncoderMotorController(port="invalid_port")

    def test_set_power_fails_on_invalid_value(self):
        """
        set_power fails if called with an invalid power value
        """
        controller = EncoderMotorController(port="M1")

        for power in (-1001, 1001):
            with self.assertRaises(ValueError):
                controller.set_power(power)

    def test_set_braking_type_fails_on_invalid_value(self):
        """
        set_braking_type fails if called with an invalid brake_type value
        """
        controller = EncoderMotorController(port="M1")

        for brake_type in (-100, -1, 2, 30):
            with self.assertRaises(ValueError):
                controller.set_braking_type(brake_type)

    def test_power_returns_none_if_not_on_mode_0(self):
        """
        power() returns None if not on Mode 0
        """
        controller = EncoderMotorController(port="M1")
        mode_mock = controller.control_mode = Mock()

        for mode in (MotorControlModes.MODE_1, MotorControlModes.MODE_2):
            mode_mock.return_value = mode
            self.assertEquals(controller.power(), None)

    def test_rpm_control_returns_none_if_not_on_mode_1(self):
        """
        rpm_control() returns None if not on Mode 1
        """
        controller = EncoderMotorController(port="M1")
        mode_mock = controller.control_mode = Mock()

        for mode in (MotorControlModes.MODE_0, MotorControlModes.MODE_2):
            mode_mock.return_value = mode
            self.assertEquals(controller.rpm_control(), None)

    def test_rpm_with_rotations_returns_none_if_not_on_mode_2(self):
        """
        rpm_with_rotations() returns None if not on Mode 1
        """
        controller = EncoderMotorController(port="M1")
        mode_mock = controller.control_mode = Mock()

        for mode in (MotorControlModes.MODE_0, MotorControlModes.MODE_1):
            mode_mock.return_value = mode
            self.assertEquals(controller.rpm_with_rotations(), None)

    def test_stop_works_on_all_modes(self):
        """
        stop() stops the motor in all modes
        """
        controller = EncoderMotorController(port="M1")
        mode_mock = controller.control_mode = Mock()

        set_power_mock = controller.set_power = Mock()
        set_rpm_control_mock = controller.set_rpm_control = Mock()
        set_rpm_with_rotations_mock = controller.set_rpm_with_rotations = Mock()

        test_data = [
            (MotorControlModes.MODE_0, set_power_mock, [0]),
            (MotorControlModes.MODE_1, set_rpm_control_mock, [0]),
            (MotorControlModes.MODE_2, set_rpm_with_rotations_mock, [0, 0])
        ]

        for mode, method_called, expected_args in test_data:
            mode_mock.return_value = mode
            controller.stop()
            method_called.assert_called_with(*expected_args)

    def test_set_braking_type_read_write(self):
        """
        Registers read/written when setting/reading braking type from MCU
        """
        for motor_port_registers in MotorControlRegisters:
            motor_port_name = motor_port_registers.name
            motor_registers = motor_port_registers.value
            brake_type_register = motor_registers[MotorRegisterTypes.BRAKE_TYPE]

            for braking_type in BrakingType:
                # create instance
                controller = EncoderMotorController(port=motor_port_name)

                # setup r/w mocks
                write_byte_mock = controller._mcu_device.write_byte = Mock()
                read_unsigned_byte_mock = controller._mcu_device.read_unsigned_byte = Mock()
                read_unsigned_byte_mock.return_value = braking_type

                # test
                controller.set_braking_type(braking_type)
                write_byte_mock.assert_called_with(brake_type_register, braking_type)

                self.assertEquals(controller.braking_type(), braking_type)
                read_unsigned_byte_mock.assert_called_with(brake_type_register)

    def test_control_mode_read_write(self):
        """
        Registers read/written when setting/reading control modes from MCU
        """
        for motor_port_registers in MotorControlRegisters:
            motor_port_name = motor_port_registers.name
            motor_registers = motor_port_registers.value
            control_mode_register = motor_registers[MotorRegisterTypes.CONTROL_MODE]

            for control_mode in MotorControlModes:
                # create instance
                controller = EncoderMotorController(port=motor_port_name)

                # setup r/w mocks
                write_byte_mock = controller._mcu_device.write_byte = Mock()
                read_unsigned_byte_mock = controller._mcu_device.read_unsigned_byte = Mock()
                read_unsigned_byte_mock.return_value = control_mode.value

                # test
                controller.set_control_mode(control_mode)
                write_byte_mock.assert_called_with(control_mode_register, control_mode.value)

                self.assertEquals(controller.control_mode(), control_mode)
                read_unsigned_byte_mock.assert_called_with(control_mode_register)

    def test_control_mode_0_read_write(self):
        """
        Registers read/written when using control mode 0 methods
        """
        power_value = 50
        for motor_port_registers in MotorControlRegisters:
            motor_port_name = motor_port_registers.name
            motor_registers = motor_port_registers.value

            mode_0_power_register = motor_registers[MotorRegisterTypes.MODE_0_POWER]

            # create instance
            controller = EncoderMotorController(port=motor_port_name)
            controller.set_control_mode = Mock()
            controller.control_mode = Mock()
            controller.control_mode.return_value = MotorControlModes.MODE_0

            # setup r/w mocks
            write_word_mock = controller._mcu_device.write_word = Mock()
            read_signed_word_mock = controller._mcu_device.read_signed_word = Mock()
            read_signed_word_mock.return_value = power_value

            # test
            controller.set_power(power_value)
            write_word_mock.assert_called_with(mode_0_power_register, power_value, little_endian=True, signed=True)

            self.assertEquals(controller.power(), power_value)
            read_signed_word_mock.assert_called_with(mode_0_power_register, little_endian=True)

    def test_control_mode_1_read_write(self):
        """
        Registers read/written  when using control mode 1 methods
        """
        rpm_value = 500
        for motor_port_registers in MotorControlRegisters:
            motor_port_name = motor_port_registers.name
            motor_registers = motor_port_registers.value

            mode_1_register = motor_registers[MotorRegisterTypes.MODE_1_RPM]

            # create instance
            controller = EncoderMotorController(port=motor_port_name)
            controller.set_control_mode = Mock()
            controller.control_mode = Mock()
            controller.control_mode.return_value = MotorControlModes.MODE_1

            # setup r/w mocks
            write_word_mock = controller._mcu_device.write_word = Mock()
            read_signed_word_mock = controller._mcu_device.read_signed_word = Mock()
            read_signed_word_mock.return_value = rpm_value

            # test
            controller.set_rpm_control(rpm_value)
            write_word_mock.assert_called_with(mode_1_register, rpm_value, little_endian=True, signed=True)

            self.assertEquals(controller.rpm_control(), rpm_value)
            read_signed_word_mock.assert_called_with(mode_1_register, little_endian=True)

    def test_control_mode_2_read_write(self):
        """
        Registers read/written  when using control mode 2 methods
        """
        rpm_value = 500
        rotations_value = 10
        # from rpm and rotations values, calculate byte values to use in mocks
        rpm_and_rotations_in_bytes = split_into_bytes(rotations_value, 2, signed=True, little_endian=True) + \
            split_into_bytes(rpm_value, 2, signed=True, little_endian=True)
        rpm_and_rotations_read = join_bytes(rpm_and_rotations_in_bytes)

        for motor_port_registers in MotorControlRegisters:
            motor_port_name = motor_port_registers.name
            motor_registers = motor_port_registers.value

            mode_1_register = motor_registers[MotorRegisterTypes.MODE_2_RPM_WITH_ROTATIONS]

            # create instance
            controller = EncoderMotorController(port=motor_port_name)
            controller.set_control_mode = Mock()
            controller.control_mode = Mock()
            controller.control_mode.return_value = MotorControlModes.MODE_2

            # setup r/w mocks
            write_n_bytes_mock = controller._mcu_device.write_n_bytes = Mock()
            read_n_unsigned_bytes_mock = controller._mcu_device.read_n_unsigned_bytes = Mock()
            read_n_unsigned_bytes_mock.return_value = rpm_and_rotations_read

            # test
            controller.set_rpm_with_rotations(rpm_value, rotations_value)
            write_n_bytes_mock.assert_called_with(mode_1_register, rpm_and_rotations_in_bytes)

            self.assertEquals(controller.rpm_with_rotations(), (rpm_value, rotations_value))
            read_n_unsigned_bytes_mock.assert_called_with(mode_1_register, 4, little_endian=True)
