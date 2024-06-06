import sys
from os import environ, listdir, path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

pytest_plugins = ("pytest_snapshot", "tests.plugins.snapshot_reporter")

# add packages to sys path so they can be imported normally in tests
packages_dir = path.join(path.dirname(__file__), "packages")
for dir in listdir(packages_dir):
    subdir = path.join(packages_dir, dir)
    sys.path.append(subdir)

# mock modules that are not installed but need to be impored
for module in [
    "pitop.common.ptdm.zmq",
    "imageio",
    "zmq",
    "zmq.green",
    "smbus2",
    "smbus",
    "atexit",
    "RPi",
    "RPi.GPIO",
    "spidev",
    "pyinotify",
]:
    sys.modules[module] = MagicMock()

# use gpiozero fake pins
environ["GPIOZERO_PIN_FACTORY"] = "mock"


@pytest.fixture
def oled_mocks():
    SIZE = (128, 64)
    MODE = "1"
    SPI_BUS = 0

    patches = {}
    patches["miniscreen_lock_file_monitor"] = patch(
        "pitop.miniscreen.miniscreen.MiniscreenLockFileMonitor"
    )
    patches["fps_regulator"] = patch("pitop.miniscreen.oled.oled.FPS_Regulator")
    patches["ptdm_sub_client"] = patch(
        "pitop.miniscreen.oled.core.device_controller.PTDMSubscribeClient"
    )
    patches["ptdm_req_client_device_controller"] = patch(
        "pitop.miniscreen.oled.core.device_controller.PTDMRequestClient"
    )
    patches["ptdm_subscribe_client_oled"] = patch(
        "pitop.miniscreen.oled.oled.PTDMSubscribeClient"
    )
    patches["ptdm_subscribe_client_miniscreen"] = patch(
        "pitop.miniscreen.miniscreen.PTDMSubscribeClient"
    )
    patches["ptlock"] = patch("pitop.miniscreen.miniscreen.PTLock")

    patches["spi_client"] = patch("pitop.miniscreen.oled.core.device_controller.spi")
    patches["sh1106_client"] = patch(
        "pitop.miniscreen.oled.core.device_controller.sh1106"
    )

    mocks = {}
    for p in patches:
        mocks[p] = patches[p].start()

    device_mock = MagicMock()
    device_mock.mode = MODE
    device_mock.size = SIZE
    device_mock.spi_bus = SPI_BUS
    device_mock.contrast = MagicMock()
    device_mock.bounding_box = (0, 0, SIZE[0] - 1, SIZE[1] - 1)

    sh1106_mock = mocks["sh1106_client"]
    sh1106_mock.return_value = device_mock

    controller = MagicMock()
    controller.get_device.return_value = sh1106_mock

    yield {
        "ptdm_req_client_mock": mocks["ptdm_req_client_device_controller"],
    }

    for p in patches:
        patches[p].stop()


@pytest.fixture
def oled(oled_mocks):
    from pitop.miniscreen.oled import OLED  # noqa: E402

    oled = OLED()
    yield oled
    del oled


@pytest.fixture
def analog_sensor_mocks():
    plate_interface_patch = patch("pitop.pma.adc_base.PlateInterface")

    from pitop.pma import LightSensor, Potentiometer, SoundSensor, UltrasonicSensor

    LightSensor.read = MagicMock(return_value=0)
    Potentiometer.read = MagicMock(return_value=0)

    # object properties are mocked differently.
    # we need to keep track of the mock object to be able to modify the returned value.
    # also, the mock  object  can't be set a s an attribute directly, since it will only store its value
    us_patch_obj = patch.object(
        UltrasonicSensor, "distance", return_value=0, new_callable=PropertyMock
    )
    us_mock_obj = us_patch_obj.start()
    UltrasonicSensor._mock = {"distance": us_mock_obj}

    ss_patch_obj = patch.object(
        SoundSensor, "reading", return_value=0, new_callable=PropertyMock
    )
    ss_mock_obj = ss_patch_obj.start()
    SoundSensor._mock = {"reading": ss_mock_obj}

    plate_interface_patch.start()

    yield {
        "light_sensor": LightSensor.read,
        "sound_sensor": SoundSensor._mock.get("reading"),
        "potentiometer": Potentiometer.read,
        "ultrasonic_sensor": UltrasonicSensor._mock.get("distance"),
    }


@pytest.fixture
def light_sensor_mock(analog_sensor_mocks):
    yield analog_sensor_mocks.get("light_sensor")


@pytest.fixture
def sound_sensor_mock(analog_sensor_mocks):
    yield analog_sensor_mocks.get("sound_sensor")


@pytest.fixture
def potentiometer_mock(analog_sensor_mocks):
    yield analog_sensor_mocks.get("potentiometer")


@pytest.fixture
def ultrasonic_sensor_mock(analog_sensor_mocks):
    yield analog_sensor_mocks.get("ultrasonic_sensor")


TESTS_FONT_DIR = f"{path.dirname(path.realpath(__file__))}/tests/fonts"
VERA_DIR = f"{TESTS_FONT_DIR}/ttf-bitstream-vera/"
ROBOTO_DIR = f"{TESTS_FONT_DIR}/roboto/"


@pytest.fixture
def fonts_mock(mocker):
    from pitop.miniscreen.oled.assistant import Fonts

    mocker.patch.object(Fonts, "_roboto_directory", ROBOTO_DIR)
    mocker.patch.object(Fonts, "_vera_directory", VERA_DIR)


@pytest.fixture
def create_sim():
    # this is used to ensure sim teardown
    from pitop.simulation import simulate

    sims = []

    def _create_sim(component, scale=None, size=None):
        sim = simulate(component, scale, size)
        sims.append(sim)
        return sim

    yield _create_sim

    for sim in sims:
        sim.stop()
