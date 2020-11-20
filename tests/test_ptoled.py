from unittest.mock import MagicMock, patch
from unittest import TestCase, main
from sys import modules, path as spath
from os import path, environ
from PIL import Image
root = path.dirname(path.dirname(path.abspath(__file__)))
spath.append(root)

modules["pitop.utils"] = MagicMock()

mock_sys_info = modules["pitop.utils.sys_info"] = MagicMock()
mock_sys_info.is_pi = MagicMock(return_value=False)

mock_curr_session_info = modules["pitop.utils.current_session_info"] = MagicMock()
mock_curr_session_info.get_first_display = MagicMock(return_value=None)

modules["pitop.utils.ptdm_message"] = MagicMock()
modules["pitop.utils.logger"] = MagicMock()
modules["zmq"] = MagicMock()
modules["numpy"] = MagicMock()
modules["RPi"] = MagicMock()
modules["RPi.GPIO"] = MagicMock()
modules["luma.core.interface.serial"] = MagicMock()
modules["luma.oled.device"] = MagicMock()

from pitop.miniscreen.oled import PTOLEDDisplay, OLEDImage  # nopep8


class PTOLEDTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        environ["SDL_VIDEODRIVER"] = "dummy"

    @classmethod
    def tearDownClass(cls):
        del environ["SDL_VIDEODRIVER"]

    def setUp(self):
        self.ptoled = PTOLEDDisplay()

    def tearDown(self):
        pass

    def get_bitmap_pix(self, file_path):
        bmp = Image.open(file_path).convert("1")
        bmp = bmp.point(lambda x: 0 if x == 0 else 1, "1")
        return self.ptoled.canvas._pil_image_to_pix_arr(bmp)

    def compare_arrays(self, func_name, canvas_pix, bmp_pix):
        print("CANVAS:")
        print(canvas_pix)
        print("BITMAP:")
        print(bmp_pix)
        self.assertEqual(canvas_pix.all(), bmp_pix.all())

    def test_image(self):
        logo_path = root + "/assets/images/pi-top.png"
        img = OLEDImage(logo_path)
        canvas_pix = self.ptoled.canvas.image(
            self.ptoled.canvas.top_left(), img)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pi-top.bmp")

        self.compare_arrays("image", canvas_pix, bmp_pix)

    def test_rectangle(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.rectangle(
            self.ptoled.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/rectangle.bmp")

        self.compare_arrays("rectangle", canvas_pix, bmp_pix)

    def test_arc(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.arc(
            self.ptoled.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/arc.bmp")

        self.compare_arrays("arc", canvas_pix, bmp_pix)

    def test_chord(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.chord(
            self.ptoled.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/chord.bmp")

        self.compare_arrays("chord", canvas_pix, bmp_pix)

    def test_ellipse(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.ellipse(
            self.ptoled.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/ellipse.bmp")

        self.compare_arrays("ellipse", canvas_pix, bmp_pix)

    def test_line(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.line(
            self.ptoled.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/line.bmp")

        self.compare_arrays("line", canvas_pix, bmp_pix)

    def test_pieslice(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.pieslice(
            self.ptoled.canvas.get_bounding_box(), 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pieslice.bmp")

        self.compare_arrays("pieslice", canvas_pix, bmp_pix)

    def test_point(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.point(
            self.ptoled.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/point.bmp")

        self.compare_arrays("point", canvas_pix, bmp_pix)

    def test_polygon(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.polygon(
            self.ptoled.canvas.get_bounding_box())
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/polygon.bmp")

        self.compare_arrays("polygon", canvas_pix, bmp_pix)

    def test_text(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.text(
            self.ptoled.canvas.top_left(), "test")
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/text.bmp")

        self.compare_arrays("text", canvas_pix, bmp_pix)

    def test_multiline_text(self):
        self.ptoled.reset()
        canvas_pix = self.ptoled.canvas.multiline_text(
            self.ptoled.canvas.top_left(), "Hello World!")
        bmp_pix = self.get_bitmap_pix(
            root + "/assets/bitmaps/multiline_text.bmp")

        self.compare_arrays("multiline_text", canvas_pix, bmp_pix)

    def test_max_fps(self):
        max_fps = 50
        self.ptoled.reset()
        self.ptoled.fps_regulator.set_max_fps(max_fps)
        max_sleep_time = self.ptoled.fps_regulator.max_sleep_time
        self.assertEqual(max_sleep_time, 1/max_fps)
