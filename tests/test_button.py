from time import sleep

import pytest
import pygame


@pytest.fixture
def make_button():
    buttons = []

    def _make_button(port="D0", name="button"):
        from pitop import Button
        button = Button(port, name=name)
        buttons.append(button)
        return button

    yield _make_button

    for button in buttons:
        button.stop_simulation()
        button.close()


def test_button(make_button):
    button = make_button()

    assert button.config == {
        "classname": "Button",
        "module": "pitop.pma.button",
        "name": "button",
        "port_name": "D0",
        "version": "0.17.0",
    }

    assert not button.value
    assert not button.state["is_pressed"]

    button.pin.drive_low()

    assert button.value
    assert button.state["is_pressed"]


def test_button_simulate(make_button, mocker, snapshot):
    mocker.patch("pitop.core.mixins.simulatable.is_virtual_hardware", return_value=True)

    button = make_button()

    button.simulate()

    # give time for the screen and sprites to be set up
    sleep(1)
    snapshot.assert_match(button.snapshot(), "default.png")

    # simulate a button click
    button.sim_event(pygame.MOUSEBUTTONDOWN, "main")

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(button.snapshot(), "button_pressed.png")

    button.sim_event(pygame.MOUSEBUTTONUP, "main")

    sleep(0.5)
    snapshot.assert_match(button.snapshot(), "default.png")


def test_button_visualize(make_button, mocker, snapshot):
    # with is_virtual_hardware False, pygame button events will not be handled
    mocker.patch("pitop.core.mixins.simulatable.is_virtual_hardware", return_value=False)

    button = make_button()

    button.simulate()

    # give time for the screen and sprites to be set up
    sleep(1)
    snapshot.assert_match(button.snapshot(), "default.png")

    # simulate a button click
    button.sim_event(pygame.MOUSEBUTTONDOWN, "main")

    # these events are a bit slow
    sleep(0.5)
    # should not have changed
    snapshot.assert_match(button.snapshot(), "default.png")

    button.pin.drive_low()
    sleep(0.1)
    snapshot.assert_match(button.snapshot(), "button_pressed.png")

    button.pin.drive_high()
    sleep(0.1)
    snapshot.assert_match(button.snapshot(), "default.png")
