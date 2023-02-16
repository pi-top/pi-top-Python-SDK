from time import sleep

import pytest


@pytest.fixture
def make_light_sensor():
    def _make_light_sensor(port="A0", name="light_sensor"):
        from pitop import LightSensor

        return LightSensor(port, name=name)

    yield _make_light_sensor


def test_light_sensor(make_light_sensor, light_sensor_mock):
    light_sensor = make_light_sensor()

    assert light_sensor.config == {
        "classname": "LightSensor",
        "module": "pitop.pma.light_sensor",
        "name": "light_sensor",
        "number_of_samples": 3,
        "port_name": "A0",
        "pin_number": 1,
        "version": "0.17.0",
    }

    assert not light_sensor.value
    assert light_sensor.state["reading"] == 0

    light_sensor_mock.return_value = 100

    assert light_sensor.value
    assert light_sensor.state["reading"] == 100


@pytest.mark.xdist_group(name="sim-group")
def test_light_sensor_simulate(
    make_light_sensor, create_sim, mocker, snapshot, light_sensor_mock
):
    mocker.patch(
        "pitop.simulation.sprites.is_virtual_hardware",
        return_value=True,
    )

    light_sensor = make_light_sensor()

    sim = create_sim(light_sensor)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "light_sensor_reads_0.png")

    # set read value to 500
    light_sensor_mock.return_value = 500

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "light_sensor_reads_500.png")

    # set read value to 999
    light_sensor_mock.return_value = 999

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "light_sensor_reads_999.png")

    # set read value to 0
    light_sensor_mock.return_value = 0
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "light_sensor_reads_0.png")
