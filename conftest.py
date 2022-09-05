from os import environ, path
from sys import modules
from unittest.mock import Mock, patch

import pytest

pytest_plugins = ("pytest_snapshot", "tests.plugins.snapshot_reporter")

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
    modules[module] = Mock()

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


TESTS_FONT_DIR = f"{path.dirname(path.realpath(__file__))}/tests/fonts"
VERA_DIR = f"{TESTS_FONT_DIR}/ttf-bitstream-vera/"
ROBOTO_DIR = f"{TESTS_FONT_DIR}/roboto/"


@pytest.fixture
def fonts_mock(mocker):
    from pitop.miniscreen.oled.assistant import Fonts

    mocker.patch.object(Fonts, "_roboto_directory", ROBOTO_DIR)
    mocker.patch.object(Fonts, "_vera_directory", VERA_DIR)
