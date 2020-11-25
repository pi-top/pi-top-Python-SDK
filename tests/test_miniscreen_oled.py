from unittest.mock import MagicMock
from unittest import TestCase
from sys import modules, path as spath
from os import path, environ
from PIL import Image
root = path.dirname(path.dirname(path.abspath(__file__)))
spath.append(root)

modules["pitopcommon"] = MagicMock()

mock_sys_info = modules["pitopcommon.sys_info"] = MagicMock()
mock_sys_info.is_pi = MagicMock(return_value=False)

mock_curr_session_info = modules["pitopcommon.current_session_info"] = MagicMock()
mock_curr_session_info.get_first_display = MagicMock(return_value=None)

modules["pitopcommon.ptdm_message"] = MagicMock()
modules["pitopcommon.logger"] = MagicMock()
modules["zmq"] = MagicMock()
modules["numpy"] = MagicMock()
modules["RPi"] = MagicMock()
modules["RPi.GPIO"] = MagicMock()
modules["luma.core.interface.serial"] = MagicMock()
modules["luma.oled.device"] = MagicMock()

# TODO: remove the need for overriding E402 check
from pitop.miniscreen.oled import OLEDDisplay, OLEDImage  # nopep8  # noqa: E402


class OLEDTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        environ["SDL_VIDEODRIVER"] = "dummy"

    @classmethod
    def tearDownClass(cls):
        del environ["SDL_VIDEODRIVER"]

    def setUp(self):
        self.oled_display = OLEDDisplay()

    def tearDown(self):
        pass

    def get_bitmap_pix(self, file_path):
        bmp = Image.open(file_path).convert("1")
        bmp = bmp.point(lambda x: 0 if x == 0 else 1, "1")
        return self.oled_display.canvas._pil_image_to_pix_arr(bmp)

    def compare_arrays(self, func_name, canvas_pix, bmp_pix):
        print("CANVAS:")
        print(canvas_pix)
        print("BITMAP:")
        print(bmp_pix)
        self.assertEqual(canvas_pix.all(), bmp_pix.all())

    def test_image(self):
        logo_path = root + "/assets/images/pi-top.png"
        img = OLEDImage(logo_path)
        canvas_pix = self.oled_display.canvas.image(
            self.oled_display.canvas.top_left(), img)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pi-top.bmp")

        self.compare_arrays("image", canvas_pix, bmp_pix)

    def test_rectangle(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.rectangle(
            self.oled_display.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/rectangle.bmp")

        self.compare_arrays("rectangle", canvas_pix, bmp_pix)

    def test_arc(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.arc(
            self.oled_display.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/arc.bmp")

        self.compare_arrays("arc", canvas_pix, bmp_pix)

    def test_chord(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.chord(
            self.oled_display.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/chord.bmp")

        self.compare_arrays("chord", canvas_pix, bmp_pix)

    def test_ellipse(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.ellipse(
            self.oled_display.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/ellipse.bmp")

        self.compare_arrays("ellipse", canvas_pix, bmp_pix)

    def test_line(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.line(
            self.oled_display.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/line.bmp")

        self.compare_arrays("line", canvas_pix, bmp_pix)

    def test_pieslice(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.pieslice(
            self.oled_display.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pieslice.bmp")

        self.compare_arrays("pieslice", canvas_pix, bmp_pix)

    def test_point(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.point(
            self.oled_display.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/point.bmp")

        self.compare_arrays("point", canvas_pix, bmp_pix)

    def test_polygon(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.polygon(
            self.oled_display.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/polygon.bmp")

        self.compare_arrays("polygon", canvas_pix, bmp_pix)

    def test_text(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.text(
            self.oled_display.canvas.top_left(), "test")
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/text.bmp")

        self.compare_arrays("text", canvas_pix, bmp_pix)

    def test_multiline_text(self):
        self.oled_display.reset()
        canvas_pix = self.oled_display.canvas.multiline_text(
            self.oled_display.canvas.top_left(), "Hello World!")
        bmp_pix = self.get_bitmap_pix(
            root + "/assets/bitmaps/multiline_text.bmp")

        self.compare_arrays("multiline_text", canvas_pix, bmp_pix)

    def test_max_fps(self):
        max_fps = 50
        self.oled_display.reset()
        self.oled_display.fps_regulator.set_max_fps(max_fps)
        max_sleep_time = self.oled_display.fps_regulator.max_sleep_time
        self.assertEqual(max_sleep_time, 1/max_fps)
