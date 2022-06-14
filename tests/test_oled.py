from unittest.mock import call

import PIL.Image
import pytest


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
        assert output_image.size == oled.size
        assert output_image.mode == oled.mode


def test_refresh_redraws_last_image(oled):
    assert oled.device.display.call_count == 2

    oled.refresh()
    assert oled.device.display.call_count == 3


def test_center_gets_screen_center(oled):
    assert oled.center == (oled.size[0] / 2, oled.size[1] / 2)


def test_top_right(oled):
    assert oled.top_right == (oled.size[0] - 1, 0)


def test_top_left(oled):
    assert oled.top_left == (0, 0)


def test_bottom_right(oled):
    assert oled.bottom_right == (oled.size[0] - 1, oled.size[1] - 1)


def test_bottom_left(oled):
    assert oled.bottom_left == (0, oled.size[1] - 1)


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
