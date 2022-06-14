import PIL.Image

MODE = "1"
SIZE = (128, 64)
LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam"""


def test_images_match():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    im_white = PIL.Image.new(MODE, SIZE, "white")
    im_black = PIL.Image.new(MODE, SIZE, "black")

    for im1, im2, match in (
        (im_white, im_white, True),
        (im_black, im_black, True),
        (im_white, im_black, False),
        (im_black, im_white, False),
    ):
        assert assistant.images_match(im1, im2) == match


def test_empty_image_output(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = assistant.empty_image
    snapshot.assert_match(to_bytes(image), "black_image.png")
    assert image.size == SIZE
    assert image.mode == MODE


def test_clear_output(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "white")
    snapshot.assert_match(to_bytes(image), "white_image.png")
    assistant.clear(image)
    snapshot.assert_match(to_bytes(image), "black_image.png")
    assert image.size == SIZE
    assert image.mode == MODE


def test_invert_output(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "white")

    snapshot.assert_match(to_bytes(image), "white_image.png")
    inverted_image = assistant.invert(image)
    snapshot.assert_match(to_bytes(inverted_image), "black_image.png")
    inverted_image = assistant.invert(inverted_image)
    snapshot.assert_match(to_bytes(inverted_image), "white_image.png")

    assert inverted_image.size == SIZE
    assert inverted_image.mode == MODE


def test_render_text_wraps(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "black")
    assistant.render_text(
        image=image,
        text=LOREM_IPSUM,
        wrap=True,
    )
    snapshot.assert_match(to_bytes(image), "wrap.png")


def test_render_text_no_wrap(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "black")
    assistant.render_text(
        image=image,
        text=LOREM_IPSUM,
        wrap=False,
    )
    snapshot.assert_match(to_bytes(image), "no-wrap.png")


def test_render_text_is_centered(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "black")
    assistant.render_text(image=image, text="Hey!")
    snapshot.assert_match(to_bytes(image), "centered.png")


def test_render_text_xy(to_bytes, snapshot, fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    image = PIL.Image.new(MODE, SIZE, "black")
    assistant.render_text(image=image, text="Hey!", xy=(0, 0))
    snapshot.assert_match(to_bytes(image), "top-left.png")


def test_recommended_text_pos():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.get_recommended_text_pos() == (SIZE[0] / 2, SIZE[1] / 2)


def test_recommended_text_anchor():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.get_recommended_text_anchor() == "mm"


def test_recommended_text_align():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.get_recommended_text_align() == "center"


def test_recommended_font_size():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.get_recommended_font_size() == 14


def test_get_recommended_font(fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)

    expected_type = PIL.ImageFont.FreeTypeFont

    for size, expected_name in (
        (None, "Roboto-Regular"),
        (4, "VeraMono"),
        (20, "Roboto-Regular"),
    ):
        recommended_font = assistant.get_recommended_font(size)
        if size is None:
            size = assistant.get_recommended_font_size()
        assert recommended_font.size == size
        assert expected_name in recommended_font.path
        assert type(recommended_font) == expected_type


def test_recommended_font_path():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    for size, expected_font_path in (
        (None, "Roboto-Regular.ttf"),
        (5, "VeraMono.ttf"),
        (20, "Roboto-Regular.ttf"),
    ):
        assert assistant.get_recommended_font_path(size) == expected_font_path


def test_regular_font(fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)

    expected_name = "Roboto-Regular"
    expected_type = PIL.ImageFont.FreeTypeFont

    for size in (None, 4, 20):
        recommended_font = assistant.get_regular_font(size)
        if size is None:
            size = assistant.get_recommended_font_size()
        assert recommended_font.size == size
        assert expected_name in recommended_font.path
        assert type(recommended_font) == expected_type


def test_regular_font_path():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.get_regular_font_path() == "Roboto-Regular.ttf"


def test_mono_font(fonts_mock):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)

    expected_name = "VeraMono"
    expected_type = PIL.ImageFont.FreeTypeFont
    for size in (None, 4, 20):
        recommended_font = assistant.get_mono_font(size=size, bold=False, italics=False)
        if size is None:
            size = assistant.get_recommended_font_size()
        assert recommended_font.size == size
        assert expected_name in recommended_font.path
        assert type(recommended_font) == expected_type


def test_mono_font_path():
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)

    for bold, italics, expected_font in (
        (True, True, "VeraMoBI.ttf"),
        (True, False, "VeraMoBd.ttf"),
        (False, True, "VeraMoIt.ttf"),
        (False, False, "VeraMono.ttf"),
    ):
        assert assistant.get_mono_font_path(bold, italics) == expected_font


def test_top_right(oled):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.top_right() == (SIZE[0] - 1, 0)


def test_top_left(oled):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.top_left() == (0, 0)


def test_bottom_right(oled):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.bottom_right() == (SIZE[0] - 1, SIZE[1] - 1)


def test_bottom_left(oled):
    from pitop.miniscreen.oled.assistant import MiniscreenAssistant

    assistant = MiniscreenAssistant(MODE, SIZE)
    assert assistant.bottom_left() == (0, SIZE[1] - 1)
