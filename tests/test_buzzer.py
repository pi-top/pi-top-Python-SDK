from time import sleep

import pytest


@pytest.fixture
def make_buzzer():
    buzzers = []

    def _make_buzzer(port="D0", name="buzzer"):
        from pitop import Buzzer

        buzzer = Buzzer(port, name=name)
        buzzers.append(buzzer)
        return buzzer

    yield _make_buzzer

    for buzzer in buzzers:
        buzzer.close()


def test_buzzer(make_buzzer):
    buzzer = make_buzzer()

    assert buzzer.config == {
        "classname": "Buzzer",
        "module": "pitop.pma.buzzer",
        "name": "buzzer",
        "port_name": "D0",
        "version": "0.17.0",
    }

    assert not buzzer.value
    assert not buzzer.state["is_active"]

    buzzer.on()

    assert buzzer.value
    assert buzzer.state["is_active"]


@pytest.mark.xdist_group(name="sim-group")
def test_buzzer_simulate(make_buzzer, create_sim, mocker, snapshot):
    mocker.patch(
        "pitop.simulation.sprites.is_virtual_hardware",
        return_value=True,
    )

    buzzer = make_buzzer()

    sim = create_sim(buzzer)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "buzzer_off.png")

    # turn buzzer on
    buzzer.on()

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "buzzer_on.png")

    # turn buzzer off
    buzzer.off()
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "buzzer_off.png")
