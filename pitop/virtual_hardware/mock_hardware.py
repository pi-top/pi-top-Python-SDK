import sys
from os import environ
from unittest.mock import patch, Mock as TMock, PropertyMock

import Mock.GPIO

from .simulation import fonts as SimFonts
from pitop.common.common_names import DeviceName

__using_virtual_hardware = False


def is_virtual_hardware():
    return __using_virtual_hardware


def use_virtual_hardware():
    global __using_virtual_hardware

    environ["GPIOZERO_PIN_FACTORY"] = "mock"

    sys.modules["RPi.GPIO"] = Mock.GPIO
    patch("pitop.system.pitop.SupportsBattery").start()
    patch("pitop.core.mixins.supports_miniscreen.device_type", return_value=DeviceName.pi_top_4.value).start()

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

    device_mock = TMock()
    device_mock.mode = MODE
    device_mock.size = SIZE
    device_mock.spi_bus = SPI_BUS
    device_mock.contrast = TMock()
    device_mock.bounding_box = (0, 0, SIZE[0] - 1, SIZE[1] - 1)

    sh1106_mock.return_value = device_mock

    controller = TMock()
    controller.get_device.return_value = sh1106_mock

    from pitop.miniscreen.oled.assistant import Fonts
    patch.object(Fonts, "_roboto_directory", SimFonts.Roboto).start()
    patch.object(Fonts, "_vera_directory", SimFonts.Vera).start()

    __using_virtual_hardware = True


if environ.get("PITOP_VIRTUAL_HARDWARE") is not None:
    use_virtual_hardware()
