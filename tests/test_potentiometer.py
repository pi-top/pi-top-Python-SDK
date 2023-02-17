from time import sleep

import pytest


@pytest.fixture
def make_potentiometer():
    def _make_potentiometer(port="A0", name="potentiometer"):
        from pitop import Potentiometer

        return Potentiometer(port, name=name)

    yield _make_potentiometer


def test_potentiometer(make_potentiometer, potentiometer_mock):
    potentiometer = make_potentiometer()

    assert potentiometer.config == {
        "classname": "Potentiometer",
        "module": "pitop.pma.potentiometer",
        "name": "potentiometer",
        "number_of_samples": 1,
        "port_name": "A0",
        "pin_number": 1,
        "version": "0.17.0",
    }

    assert not potentiometer.value
    assert potentiometer.state["position"] == 0

    potentiometer_mock.return_value = 100

    assert potentiometer.value
    assert potentiometer.state["position"] == 100


@pytest.mark.skip
@pytest.mark.xdist_group(name="sim-group")
def test_potentiometer_simulate(
    make_potentiometer, create_sim, mocker, snapshot, potentiometer_mock
):
    mocker.patch(
        "pitop.simulation.sprites.is_virtual_hardware",
        return_value=True,
    )

    potentiometer = make_potentiometer()

    sim = create_sim(potentiometer)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "potentiometer_reads_0.png")

    # set read value to 500
    potentiometer_mock.return_value = 500

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "potentiometer_reads_500.png")

    # set read value to 999
    potentiometer_mock.return_value = 999

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "potentiometer_reads_999.png")

    # set read value to 0
    potentiometer_mock.return_value = 0
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "potentiometer_reads_0.png")
