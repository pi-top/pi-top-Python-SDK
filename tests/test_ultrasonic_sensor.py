from time import sleep

import pytest


@pytest.fixture
def make_ultrasonic_sensor():
    ultrasonic_sensors = []

    def _make_ultrasonic_sensor(port="D0", name="ultrasonic_sensor"):
        from pitop import UltrasonicSensor

        us = UltrasonicSensor(port, name=name)
        ultrasonic_sensors.append(us)
        return us

    yield _make_ultrasonic_sensor

    for us in ultrasonic_sensors:
        us.close()


def test_ultrasonic_sensor(make_ultrasonic_sensor, ultrasonic_sensor_mock):
    ultrasonic_sensor = make_ultrasonic_sensor()

    assert ultrasonic_sensor.config == {
        "classname": "UltrasonicSensor",
        "module": "pitop.pma.ultrasonic_sensor",
        "name": "ultrasonic_sensor",
        "port_name": "D0",
        "partial": False,
        "max_distance": 3,
        "queue_len": 5,
        "threshold_distance": 0.3,
        "version": "0.17.0",
    }

    assert ultrasonic_sensor.state["distance"] == 0

    ultrasonic_sensor_mock.return_value = 100

    assert ultrasonic_sensor.state["distance"] == 100


@pytest.mark.simulationtest
def test_ultrasonic_sensor_simulate(
    make_ultrasonic_sensor, create_sim, mocker, snapshot, ultrasonic_sensor_mock
):
    mocker.patch(
        "pitop.simulation.sprites.is_virtual_hardware",
        return_value=True,
    )

    ultrasonic_sensor = make_ultrasonic_sensor()

    sim = create_sim(ultrasonic_sensor)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "ultrasonic_sensor_reads_0.png")

    # set read value to 1
    ultrasonic_sensor_mock.return_value = 1

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "ultrasonic_sensor_reads_1.png")

    # set read value to 3
    ultrasonic_sensor_mock.return_value = 3

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "ultrasonic_sensor_reads_3.png")

    # set read value to 0
    ultrasonic_sensor_mock.return_value = 0
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "ultrasonic_sensor_reads_0.png")
