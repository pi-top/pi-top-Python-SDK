from unittest.mock import patch
from time import sleep

import pytest
import pygame

from tests.utils import snapshot_simulation


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
    mocker.patch("pitop.pma.button.using_virtual_hardware", new=True)

    from pitop import Pitop
    from pitop.pma import LED, Button

    pitop = Pitop()
    pitop.add_component(LED("D0"))
    pitop.add_component(Button("D1"))

    pitop.button.when_pressed = pitop.led.on
    pitop.button.when_released = pitop.led.off

    pitop.simulate()

    # give time for the screen and sprites to be set up
    sleep(0.5)
    snapshot.assert_match(snapshot_simulation(pitop), "default.png")

    # simulate a button click
    pos = (pitop.button._sprite.rect.x, pitop.button._sprite.rect.y)
    #pygame.mouse.set_pos(pos)

    mouse_motion_event = pygame.fastevent.Event(pygame.MOUSEMOTION, {'pos': pos, 'rel': pos, 'buttons': (0, 0, 0), 'touch': False, 'window': None})
    pygame.fastevent.post(mouse_motion_event)

    mouse_down_event = pygame.fastevent.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
    pygame.fastevent.post(mouse_down_event)

    sleep(0.1)
    snapshot.assert_match(snapshot_simulation(pitop), "button_pressed.png")

    mouse_up_event = pygame.fastevent.Event(pygame.MOUSEBUTTONUP, {'pos': pos, 'button': 1, 'touch': False, 'window': None})
    pygame.fastevent.post(mouse_up_event)

    sleep(0.1)
    snapshot.assert_match(snapshot_simulation(pitop), "button_released.png")

    # delete refs to trigger component cleanup
    pitop.stop_simulation()
    del pitop
    del Pitop.instance
