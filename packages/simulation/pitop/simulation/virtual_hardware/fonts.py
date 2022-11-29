from unittest.mock import patch

from pygame import font


def mock_fonts():
    fonts = font.get_fonts()

    have_roboto = any([1 for f in fonts if "roboto" in f])
    have_vera = any([1 for f in fonts if "vera" in f])

    sans_fonts = [f for f in fonts if "sans" in f and "mono" not in f]
    default_sans = sans_fonts[0] if len(sans_fonts) else fonts[0]

    mono_fonts = [f for f in fonts if "mono" in f]
    default_mono = mono_fonts[0] if len(mono_fonts) else fonts[0]

    if not have_roboto:
        fallback = font.match_font(default_sans)
        patch(
            "pitop.miniscreen.oled.assistant.Fonts.regular", return_value=fallback
        ).start()

    if not have_vera:

        def mono(bold, italics):
            return font.match_font(default_mono, bold, italics)

        patch("pitop.miniscreen.oled.assistant.Fonts.mono", mono).start()
