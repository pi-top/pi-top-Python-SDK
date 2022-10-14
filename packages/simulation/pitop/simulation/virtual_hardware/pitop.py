from unittest.mock import Mock, patch

from pitop.common.common_names import DeviceName
from .fonts import mock_fonts

def mock_pitop():
    patch("pitop.system.pitop.SupportsBattery").start()
    patch(
        "pitop.core.mixins.supports_miniscreen.device_type",
        return_value=DeviceName.pi_top_4.value,
    ).start()

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
    ptdm_req_client_patch.start()
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

    mock_fonts()
