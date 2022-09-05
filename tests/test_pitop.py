import tkinter
from unittest.mock import patch

import pytest

from tests.utils import create_widget_mock, snapshot_simulation


@pytest.fixture
def pitop_mocks():
    mocks = {}

    mocks["supports_miniscreen"] = patch("pitop.system.pitop.SupportsMiniscreen")
    mocks["supports_miniscreen"].start()

    mocks["supports_battery"] = patch("pitop.system.pitop.SupportsBattery")
    mocks["supports_battery"].start()

    mocks["encoder_motor_controller"] = patch(
        "pitop.pma.encoder_motor.EncoderMotorController"
    )
    mocks["encoder_motor_controller"].start()

    from pitop.pma import EncoderMotor

    mocks["rotation_counter"] = patch.object(EncoderMotor, "rotation_counter")
    mocks["rotation_counter"].start()

    mocks["braking_type"] = patch.object(EncoderMotor, "braking_type").start()
    mocks["braking_type"].start()

    mocks["set_target_speed"] = patch.object(EncoderMotor, "set_target_speed")
    mocks["set_target_speed"].start()

    yield mocks

    mocks["supports_miniscreen"].stop()
    mocks["supports_battery"].stop()
    mocks["encoder_motor_controller"].stop()
    mocks["rotation_counter"].stop()
    mocks["braking_type"].stop()
    mocks["set_target_speed"].stop()


def test_pitop(pitop_mocks):
    from pitop import Pitop
    from pitop.pma import LED
    from pitop.robotics.drive_controller import DriveController

    pitop = Pitop()
    drive = DriveController()
    pitop.add_component(drive)
    led = LED("D0")
    pitop.add_component(led)

    assert pitop.config == {
        "classname": "Pitop",
        "components": {
            "drive": {
                "classname": "DriveController",
                "left_motor_port": "M3",
                "module": "pitop.robotics.drive_controller",
                "name": "drive",
                "right_motor_port": "M0",
                "version": "0.17.0",
            },
            "led": {
                "classname": "LED",
                "module": "pitop.pma.led",
                "name": "led",
                "port_name": "D0",
                "version": "0.17.0",
            },
        },
        "module": "pitop.system.pitop",
        "version": "0.17.0",
    }

    assert not pitop.state["led"]["is_lit"]

    pitop.led.on()

    assert pitop.state["led"]["is_lit"]

    pitop.drive.forward(50)

    pitop.drive.left_motor.set_target_speed.assert_called()
    pitop.drive.right_motor.set_target_speed.assert_called()

    # delete refs to trigger component cleanup
    del pitop
    del Pitop.instance


def test_blockpi_rover(pitop_mocks):
    from pitop import BlockPiRover

    rover = BlockPiRover()

    assert rover.config == {
        "classname": "BlockPiRover",
        "components": {
            "drive": {
                "classname": "DriveController",
                "left_motor_port": "M3",
                "module": "pitop.robotics.drive_controller",
                "name": "drive",
                "right_motor_port": "M0",
                "version": "0.17.0",
            },
        },
        "module": "pitop.robotics.blockpi_rover",
        "version": "0.17.0",
    }

    rover.forward(50)

    rover.drive.left_motor.set_target_speed.assert_called()
    rover.drive.right_motor.set_target_speed.assert_called()

    # delete refs to trigger component cleanup
    del rover
    del BlockPiRover.instance


def test_pitop_virtualize(pitop_mocks, mocker, snapshot):
    mocker.patch("pitop.pma.button.TkInterButton", create_widget_mock(tkinter.Button))

    from pitop import Pitop
    from pitop.pma import LED, Button

    pitop = Pitop()
    pitop.add_component(LED("D0"))
    pitop.add_component(Button("D1"))

    pitop.button.when_pressed = lambda: pitop.led.on()  # noqa: F821
    pitop.button.when_released = lambda: pitop.led.off()  # noqa: F821

    pitop.simulate()

    snapshot.assert_match(snapshot_simulation(pitop), "default.png")

    # delete refs to trigger component cleanup
    pitop.stop_simulation()
    del pitop
    del Pitop.instance
