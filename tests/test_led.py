from time import sleep

import pytest
import pygame


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

    led.close()


def test_led_simulate(snapshot):
    from pitop import LED

    led = LED("D0")

    led.simulate()

    # give time for the screen and sprites to be set up
    sleep(0.5)
    snapshot.assert_match(led.snapshot(), "default.png")

    led.on()

    sleep(0.1)
    snapshot.assert_match(led.snapshot(), "led_on.png")

    led.off()

    sleep(0.1)
    snapshot.assert_match(led.snapshot(), "default.png")

    led.stop_simulation()
    led.close()

def test_led_color(snapshot):
    from pitop import LED

    red_led = LED("D0")
    green_led = LED("D1", color="green")
    yellow_led = LED("D2", color="yellow")

    assert red_led.color == "red"
    assert green_led.color == "green"
    assert yellow_led.color == "yellow"

    red_led.simulate()
    green_led.simulate()
    yellow_led.simulate()

    # give time for the screen and sprites to be set up
    sleep(0.5)
    snapshot.assert_match(red_led.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_off.png")

    red_led.on()
    gree_led.on()
    yellow_led.on()

    sleep(0.1)
    snapshot.assert_match(red_led.snapshot(), "red_led_on.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_on.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_on.png")

    led.off()

    sleep(0.1)
    snapshot.assert_match(red_led.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_off.png")

    red_led.stop_simulation()
    green_led.stop_simulation()
    yellow_led.stop_simulation()
    red_led.close()
    gree_led.close()
    yellow_led.close()
