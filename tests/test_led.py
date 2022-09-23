from time import sleep

import pytest
import pygame


@pytest.fixture
def make_led():
    leds = []

    def _make_led(port="D0", name="led", color=None):
        from pitop import LED
        led = LED(port, name=name, color=color)
        leds.append(led)
        return led

    yield _make_led

    for led in leds:
        led.stop_simulation()
        led.close()


def test_led(make_led):
    led = make_led()

    assert led.config == {
        "classname": "LED",
        "color": "red",
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


def test_led_simulate(make_led, snapshot):
    led = make_led()

    led.simulate()

    # give time for the screen and sprites to be set up
    sleep(1)
    snapshot.assert_match(led.snapshot(), "default.png")

    led.on()

    sleep(0.1)
    snapshot.assert_match(led.snapshot(), "led_on.png")

    led.off()

    sleep(0.1)
    snapshot.assert_match(led.snapshot(), "default.png")

def test_led_color(make_led, snapshot):
    red_led = make_led("D0")
    green_led = make_led("D1", color="green")
    yellow_led = make_led("D2", color="yellow")

    assert red_led.color == "red"
    assert green_led.color == "green"
    assert yellow_led.color == "yellow"

    red_led.simulate()
    green_led.simulate()
    yellow_led.simulate()

    # give time for the screen and sprites to be set up
    sleep(1)
    snapshot.assert_match(red_led.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_off.png")

    red_led.on()
    green_led.on()
    yellow_led.on()

    sleep(0.1)
    snapshot.assert_match(red_led.snapshot(), "red_led_on.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_on.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_on.png")

    red_led.off()
    green_led.off()
    yellow_led.off()

    sleep(0.1)
    snapshot.assert_match(red_led.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_led.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_led.snapshot(), "yellow_led_off.png")
