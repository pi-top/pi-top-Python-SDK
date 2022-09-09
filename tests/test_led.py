from time import sleep

import pytest
import pygame

from tests.utils import snapshot_simulation


def test_led():
    from pitop import LED

    led = LED("D0")

    assert led.config == {
        "classname": "LED",
        "module": "pitop.pma.led",
        "name": "led",
        "port_name": "D0",
        "version": "0.17.0",
    }

    assert not led.value
    assert not led.state["is_lit"]

    led.on()

    assert led.value
    assert led.state["is_lit"]

    # delete ref to trigger component cleanup
    led.close()


def test_led_simulate(snapshot):
    from pitop import LED

    led = LED("D0")

    led.simulate()

    # give time for the screen and sprites to be set up
    sleep(0.5)
    snapshot.assert_match(snapshot_simulation(led), "default.png")

    led.on()

    sleep(0.1)
    snapshot.assert_match(snapshot_simulation(led), "led_on.png")

    led.off()

    sleep(0.1)
    snapshot.assert_match(snapshot_simulation(led), "default.png")

    led.stop_simulation()
    # delete ref to trigger component cleanup
    del led
