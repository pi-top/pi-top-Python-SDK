from os import path
from unittest.mock import MagicMock, call

import PIL.Image
import pytest

from tests.utils import to_bytes


@pytest.mark.parametrize("contrast_value", ("123", -100, -1, 257))
def test_contrast_raises_on_invalid_values(oled, contrast_value):
    with pytest.raises(AssertionError):
        oled.contrast(contrast_value)


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


@pytest.mark.parametrize(
    "image,expected_output",
    (
        (None, False),
        (PIL.Image.new("1", (15, 34), "white"), True),
        (PIL.Image.new("1", (128, 64), "white"), True),
        (PIL.Image.new("1", (128, 64), "black"), False),
    ),
)
def test_should_redisplay_output(oled, image, expected_output):
    assert oled.should_redisplay(image_to_display=image) is expected_output


@pytest.mark.parametrize(
    "input_image",
    (
        PIL.Image.new("1", (24, 123), "white"),
        PIL.Image.new("L", (224, 13), "black"),
    ),
)
def test_prepare_image_transforms_images(oled, input_image):
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


@pytest.mark.parametrize("bus", (-1, 2, 10))
def test_spi_bus_setter_validates_input(oled, bus):
    with pytest.raises(AssertionError):
        oled.spi_bus = bus


def test_spi_bus_setter_sends_ptdm_request(oled_mocks, oled):
    ptdm_req_client_mock = oled_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.spi_bus = 0
    assert ptdm_req_client_mock.call_count > 2


def test_set_control_to_pi_sends_ptdm_request(oled_mocks, oled):
    ptdm_req_client_mock = oled_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.set_control_to_pi()
    assert ptdm_req_client_mock.call_count > 2


def test_set_control_to_hub_sends_ptdm_request(oled_mocks, oled):
    ptdm_req_client_mock = oled_mocks.get("ptdm_req_client_mock")

    assert ptdm_req_client_mock.call_count == 2
    oled.set_control_to_hub()
    assert ptdm_req_client_mock.call_count > 2


def test_show_and_hide_changes_visible_property(oled):
    assert oled.visible is True
    oled.show()
    assert oled.visible is False
    oled.hide()
    assert oled.visible is True


def test_clear_displays_an_empty_image(oled, snapshot):
    sample_image_path = (
        f"{path.dirname(path.realpath(__file__))}/assets/miniscreen/sample.png"
    )

    oled.display_image_file(sample_image_path)
    snapshot.assert_match(to_bytes(oled.image), "sample_image.png")
    oled.clear()
    snapshot.assert_match(to_bytes(oled.image), "black_image.png")


def test_refresh_restores_control_and_resets(oled):
    oled._controller.set_control_to_pi = MagicMock()
    oled._controller.reset_device = MagicMock()
    assert oled._controller.set_control_to_pi.call_count == 0
    assert oled._controller.reset_device.call_count == 0

    oled.reset()

    assert oled._controller.set_control_to_pi.call_count == 1
    assert oled._controller.reset_device.call_count == 1


def test_display_image_file(oled, snapshot):
    sample_image_path = (
        f"{path.dirname(path.realpath(__file__))}/assets/miniscreen/sample.png"
    )

    oled.display_image_file(sample_image_path)
    snapshot.assert_match(to_bytes(oled.image), "sample_image.png")


def test_display_image(oled, snapshot):
    sample_image_path = (
        f"{path.dirname(path.realpath(__file__))}/assets/miniscreen/sample.png"
    )
    image = PIL.Image.open(sample_image_path)

    oled.display_image(image)
    snapshot.assert_match(to_bytes(oled.image), "sample_image.png")


def test_display_text_with_long_text(oled, snapshot, fonts_mock):
    text = "Hey! This is a super long line"

    oled.display_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")

    oled.display_text(text, font_size=8)
    snapshot.assert_match(to_bytes(oled.image), "small_font_size.png")

    oled.display_text(text, font_size=20)
    snapshot.assert_match(to_bytes(oled.image), "large_font_size.png")

    oled.display_text(text, invert=True)
    snapshot.assert_match(to_bytes(oled.image), "invert.png")

    oled.display_text(text, xy=(20, 40))
    snapshot.assert_match(to_bytes(oled.image), "xy.png")

    oled.display_text(text, anchor="rs")
    snapshot.assert_match(to_bytes(oled.image), "anchor.png")


def test_display_text_with_short_text(oled, snapshot, fonts_mock):
    text = "Hey!"

    oled.display_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")

    oled.display_text(text, font_size=8)
    snapshot.assert_match(to_bytes(oled.image), "small_font_size.png")

    oled.display_text(text, font_size=20)
    snapshot.assert_match(to_bytes(oled.image), "large_font_size.png")

    oled.display_text(text, invert=True)
    snapshot.assert_match(to_bytes(oled.image), "invert.png")

    oled.display_text(text, xy=(20, 40))
    snapshot.assert_match(to_bytes(oled.image), "xy.png")

    oled.display_text(text, anchor="rs")
    snapshot.assert_match(to_bytes(oled.image), "anchor.png")


def test_display_multiline_text_with_short_text(oled, snapshot, fonts_mock):
    text = "Hey!"

    oled.display_multiline_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")

    oled.display_multiline_text(text, font_size=8)
    snapshot.assert_match(to_bytes(oled.image), "small_font_size.png")

    oled.display_multiline_text(text, font_size=20)
    snapshot.assert_match(to_bytes(oled.image), "large_font_size.png")

    oled.display_multiline_text(text, invert=True)
    snapshot.assert_match(to_bytes(oled.image), "invert.png")

    oled.display_multiline_text(text, xy=(20, 40))
    snapshot.assert_match(to_bytes(oled.image), "xy.png")

    oled.display_multiline_text(text, anchor="rs")
    snapshot.assert_match(to_bytes(oled.image), "anchor.png")


def test_display_multiline_text_with_long_text(oled, snapshot, fonts_mock):
    text = "Hey! This is a super long line"

    oled.display_multiline_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")

    oled.display_multiline_text(text, font_size=8)
    snapshot.assert_match(to_bytes(oled.image), "small_font_size.png")

    oled.display_multiline_text(text, font_size=20)
    snapshot.assert_match(to_bytes(oled.image), "large_font_size.png")

    oled.display_multiline_text(text, invert=True)
    snapshot.assert_match(to_bytes(oled.image), "invert.png")

    oled.display_multiline_text(text, xy=(20, 40))
    snapshot.assert_match(to_bytes(oled.image), "xy.png")

    oled.display_multiline_text(text, anchor="rs")
    snapshot.assert_match(to_bytes(oled.image), "anchor.png")


def test_display_text_with_newlines(oled, snapshot, fonts_mock):
    # display_text prints newlines
    text = "Line1\nLine2\nLine3\nLine4"
    oled.display_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")


def test_display_multiline_text_with_newlines(oled, snapshot, fonts_mock):
    # display_multiline_text automatically wraps text, omits newlines from input
    text = "Line1\nLine2\nLine3\nLine4"
    oled.display_multiline_text(text)
    snapshot.assert_match(to_bytes(oled.image), "defaults.png")


def test_subscribes_to_pitopd_ready_event(oled):
    from pitop.common.ptdm import Message

    callback = oled._ptdm_subscribe_client._callback_funcs.get(Message.PUB_PITOPD_READY)
    assert callback is not None
