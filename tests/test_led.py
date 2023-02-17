from time import sleep

import pytest


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


@pytest.mark.skip
@pytest.mark.xdist_group(name="sim-group")
def test_led_simulate(make_led, create_sim, snapshot):
    led = make_led()

    sim = create_sim(led)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "default.png")

    led.on()

    sleep(0.1)
    snapshot.assert_match(sim.snapshot(), "led_on.png")

    led.off()

    sleep(0.1)
    snapshot.assert_match(sim.snapshot(), "default.png")


@pytest.mark.skip
@pytest.mark.xdist_group(name="sim-group")
def test_led_color(make_led, create_sim, snapshot):
    red_led = make_led("D0")
    green_led = make_led("D1", color="green")
    yellow_led = make_led("D2", color="yellow")

    assert red_led.color == "red"
    assert green_led.color == "green"
    assert yellow_led.color == "yellow"

    red_sim = create_sim(red_led)
    green_sim = create_sim(green_led)
    yellow_sim = create_sim(yellow_led)

    # give time for the screen and sprites to be set up
    sleep(3)
    snapshot.assert_match(red_sim.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_sim.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_sim.snapshot(), "yellow_led_off.png")

    red_led.on()
    green_led.on()
    yellow_led.on()

    sleep(0.2)
    snapshot.assert_match(red_sim.snapshot(), "red_led_on.png")
    snapshot.assert_match(green_sim.snapshot(), "green_led_on.png")
    snapshot.assert_match(yellow_sim.snapshot(), "yellow_led_on.png")

    red_led.off()
    green_led.off()
    yellow_led.off()

    sleep(0.2)
    snapshot.assert_match(red_sim.snapshot(), "red_led_off.png")
    snapshot.assert_match(green_sim.snapshot(), "green_led_off.png")
    snapshot.assert_match(yellow_sim.snapshot(), "yellow_led_off.png")


@pytest.mark.skip
@pytest.mark.xdist_group(name="sim-group")
def test_led_sim_scale(make_led, create_sim, snapshot):
    led = make_led()

    sim = create_sim(led, 2, (80, 160))

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "default.png")
