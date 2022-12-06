from time import sleep

import pytest


@pytest.fixture
def make_sound_sensor():
    def _make_sound_sensor(port="A0", name="sound_sensor"):
        from pitop import SoundSensor

        return SoundSensor(port, name=name)

    yield _make_sound_sensor


def test_sound_sensor(make_sound_sensor, sound_sensor_mock):
    sound_sensor = make_sound_sensor()

    assert sound_sensor.config == {
        "classname": "SoundSensor",
        "module": "pitop.pma.sound_sensor",
        "name": "sound_sensor",
        "number_of_samples": 1,
        "port_name": "A0",
        "pin_number": 1,
        "version": "0.17.0",
    }

    assert not sound_sensor.value
    assert sound_sensor.state["reading"] == 0

    sound_sensor_mock.return_value = 100

    assert sound_sensor.value
    assert sound_sensor.state["reading"] == 100


def test_sound_sensor_simulate(
    make_sound_sensor, create_sim, mocker, snapshot, sound_sensor_mock
):
    mocker.patch(
        "pitop.simulation.sprites.is_virtual_hardware",
        return_value=True,
    )

    sound_sensor = make_sound_sensor()

    sim = create_sim(sound_sensor)

    # give time for the screen and sprites to be set up
    sleep(2)
    snapshot.assert_match(sim.snapshot(), "sound_sensor_reads_0.png")

    # set read value to 250
    sound_sensor_mock.return_value = 250

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "sound_sensor_reads_250.png")

    # set read value to 500
    sound_sensor_mock.return_value = 500

    # these events are a bit slow
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "sound_sensor_reads_500.png")

    # set read value to 0
    sound_sensor_mock.return_value = 0
    sleep(0.5)
    snapshot.assert_match(sim.snapshot(), "sound_sensor_reads_0.png")
