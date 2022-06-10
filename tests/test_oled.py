from unittest.mock import Mock, call, patch

import PIL.Image
import pytest

SIZE = (128, 64)
MODE = "1"
SPI_BUS = 0


@pytest.fixture
def setup_mocks():
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
    # device_mock.display = Mock()

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
def oled(setup_mocks):
    yield setup_mocks.get("oled")


def test_contrast_raises_on_invalid_values(oled):
    for value in ("123", -100, -1, 257):
        with pytest.raises(AssertionError):
            oled.contrast(value)


def test_contrast_is_set_on_instantiation(oled):
    oled.device.contrast.assert_called_once_with(255)


def test_wake_sets_contrast(oled):
    oled.wake()

    oled.device.contrast.assert_has_calls(
        [
            call(255),
            call(255),
        ]
    )


def test_sleep_sets_contrast(oled):
    oled.sleep()

    oled.device.contrast.assert_has_calls(
        [
            call(255),
            call(0),
        ]
    )


def test_should_redisplay_output(oled):

    for image, expected_output in [
        (None, False),
        (PIL.Image.new("1", (1, 1), "white"), True),
        (PIL.Image.new("1", (128, 64), "white"), True),
        (PIL.Image.new("1", (128, 64), "black"), False),
    ]:
        assert oled.should_redisplay(image_to_display=image) is expected_output


def test_prepare_image_transforms_images(oled):

    for input_image in [
        PIL.Image.new("1", (24, 123), "white"),
        PIL.Image.new("L", (224, 13), "black"),
    ]:
        output_image = oled.prepare_image(image_to_prepare=input_image)
        assert output_image.size == SIZE
        assert output_image.mode == MODE


def test_refresh_redraws_last_image(oled):
    assert oled.device.display.call_count == 2

    oled.refresh()
    assert oled.device.display.call_count == 3


def test_center_gets_screen_center(oled):
    assert oled.center == (SIZE[0] / 2, SIZE[1] / 2)


def test_top_right(oled):
    assert oled.top_right == (SIZE[0] - 1, 0)


def test_top_left(oled):
    assert oled.top_left == (0, 0)


def test_bottom_right(oled):
    assert oled.bottom_right == (SIZE[0] - 1, SIZE[1] - 1)


def test_bottom_left(oled):
    assert oled.bottom_left == (0, SIZE[1] - 1)


def test_spi_bus_setter_validates_input(oled):
    for bus in (-1, 2, 10):
        with pytest.raises(AssertionError):
            oled.spi_bus = bus


def test_spi_bus_setter_sends_ptdm_request(setup_mocks):
    oled = setup_mocks.get("oled")
    ptdm_req_client_mock = setup_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.spi_bus = 0
    assert ptdm_req_client_mock.call_count > 2


def test_set_control_to_pi_sends_ptdm_request(setup_mocks):
    oled = setup_mocks.get("oled")
    ptdm_req_client_mock = setup_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.set_control_to_pi()
    assert ptdm_req_client_mock.call_count > 2


def test_set_control_to_hub_sends_ptdm_request(setup_mocks):
    oled = setup_mocks.get("oled")
    ptdm_req_client_mock = setup_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.set_control_to_hub()
    assert ptdm_req_client_mock.call_count > 2
