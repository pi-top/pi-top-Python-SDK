import sys
from os import environ, listdir, path
from unittest.mock import Mock, PropertyMock, patch

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
    "smbus2",
    "smbus",
    "atexit",
    "RPi",
    "RPi.GPIO",
    "spidev",
    "pyinotify",
]:
    sys.modules[module] = Mock()

# use gpiozero fake pins
environ["GPIOZERO_PIN_FACTORY"] = "mock"


@pytest.fixture
def oled_mocks():
    SIZE = (128, 64)
    MODE = "1"
    SPI_BUS = 0

    miniscreen_lock_file_monitor_patch = patch(
        "pitop.miniscreen.oled.oled.MiniscreenLockFileMonitor"
    )
    fps_regulator_patch = patch("pitop.miniscreen.oled.oled.FPS_Regulator")
    ptdm_sub_client_patch = patch(
        "pitop.miniscreen.oled.core.device_controller.PTDMSubscribeClient"
    )
    ptdm_req_client_patch = patch(
        "pitop.miniscreen.oled.core.device_controller.PTDMRequestClient"
    )
    ptlock_patch = patch("pitop.miniscreen.oled.core.device_controller.PTLock")

    spi_client_patch = patch("pitop.miniscreen.oled.core.device_controller.spi")
    sh1106_client_patch = patch("pitop.miniscreen.oled.core.device_controller.sh1106")

    miniscreen_lock_file_monitor_patch.start()
    fps_regulator_patch.start()
    ptdm_sub_client_patch.start()
    ptdm_req_client_mock = ptdm_req_client_patch.start()
    ptlock_patch.start()
    spi_client_patch.start()
    sh1106_mock = sh1106_client_patch.start()

    device_mock = Mock()
    device_mock.mode = MODE
    device_mock.size = SIZE
    device_mock.spi_bus = SPI_BUS
    device_mock.contrast = Mock()
    device_mock.bounding_box = (0, 0, SIZE[0] - 1, SIZE[1] - 1)

    sh1106_mock.return_value = device_mock

    controller = Mock()
    controller.get_device.return_value = sh1106_mock

    from pitop.miniscreen.oled import OLED  # noqa: E402

    oled = OLED()

    yield {
        "oled": oled,
        "ptdm_req_client_mock": ptdm_req_client_mock,
    }

    miniscreen_lock_file_monitor_patch.stop()
    fps_regulator_patch.stop()
    ptdm_sub_client_patch.stop()
    ptdm_req_client_patch.stop()
    ptlock_patch.stop()
    spi_client_patch.stop()
    sh1106_client_patch.stop()


@pytest.fixture
def oled(oled_mocks):
    yield oled_mocks.get("oled")


@pytest.fixture
def analog_sensor_mocks():
    plate_interface_patch = patch("pitop.pma.adc_base.PlateInterface")

    from pitop.pma import LightSensor, Potentiometer, SoundSensor, UltrasonicSensor

    LightSensor.read = Mock(return_value=0)
    Potentiometer.read = Mock(return_value=0)

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
