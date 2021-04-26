from sys import modules
from unittest.mock import MagicMock

mock_sys_info = modules["pitopcommon.sys_info"] = MagicMock()
mock_sys_info.is_pi = MagicMock(return_value=False)

mock_curr_session_info = modules["pitopcommon.current_session_info"] = MagicMock()
mock_curr_session_info.get_first_display = MagicMock(return_value=None)

modules_to_patch = [
    "PIL",
    "luma.core.interface.serial",
    "luma.oled.device",
    "pyinotify",
    "pitop.camera",
    "numpy",
    "pitopcommon.smbus_device",
    "pitopcommon.logger",
    "pitopcommon.singleton",
    "pitopcommon.common_ids",
    "pitopcommon.current_session_info",
    "pitopcommon.ptdm",
    "pitopcommon.firmware_device",
    "pitopcommon.command_runner",
    "pitopcommon.common_names",

]
for module in modules_to_patch:
    modules[module] = MagicMock()

from pitop.miniscreen import Miniscreen
from unittest import TestCase, skip
from PIL import Image
from os import environ, path

# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


root = path.dirname(path.dirname(path.abspath(__file__)))


@skip
class OLEDTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        environ["SDL_VIDEODRIVER"] = "dummy"

    @classmethod
    def tearDownClass(cls):
        del environ["SDL_VIDEODRIVER"]

    def setUp(self):
        self.miniscreen = Miniscreen()

    def tearDown(self):
        pass

    def get_bitmap_pix(self, file_path):
        bmp = Image.open(file_path).convert("1")
        bmp = bmp.point(lambda x: 0 if x == 0 else 1, "1")
        return self.miniscreen.core.canvas._pil_image_to_pix_arr(bmp)

    def compare_arrays(self, func_name, canvas_pix, bmp_pix):
        print("CANVAS:")
        print(canvas_pix)
        print("BITMAP:")
        print(bmp_pix)
        self.assertEqual(canvas_pix.all(), bmp_pix.all())

    def test_image(self):
        logo_path = root + "/assets/images/pi-top.png"
        img = Image.open(logo_path)
        canvas_pix = self.miniscreen.core.canvas.image(
            self.miniscreen.core.canvas.top_left(), img)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pi-top.bmp")

        self.compare_arrays("image", canvas_pix, bmp_pix)

    def test_rectangle(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.rectangle(
            self.miniscreen.bounding_box)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/rectangle.bmp")

        self.compare_arrays("rectangle", canvas_pix, bmp_pix)

    def test_arc(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.arc(
            self.miniscreen.bounding_box, 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/arc.bmp")

        self.compare_arrays("arc", canvas_pix, bmp_pix)

    def test_chord(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.chord(
            self.miniscreen.bounding_box, 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/chord.bmp")

        self.compare_arrays("chord", canvas_pix, bmp_pix)

    def test_ellipse(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.ellipse(
            self.miniscreen.bounding_box)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/ellipse.bmp")

        self.compare_arrays("ellipse", canvas_pix, bmp_pix)

    def test_line(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.line(
            self.miniscreen.bounding_box)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/line.bmp")

        self.compare_arrays("line", canvas_pix, bmp_pix)

    def test_pieslice(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.pieslice(
            self.miniscreen.bounding_box, 0, 180)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/pieslice.bmp")

        self.compare_arrays("pieslice", canvas_pix, bmp_pix)

    def test_point(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.point(
            self.miniscreen.bounding_box)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/point.bmp")

        self.compare_arrays("point", canvas_pix, bmp_pix)

    def test_polygon(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.polygon(
            self.miniscreen.bounding_box)
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/polygon.bmp")

        self.compare_arrays("polygon", canvas_pix, bmp_pix)

    def test_text(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.text(
            self.miniscreen.core.canvas.top_left(), "test")
        bmp_pix = self.get_bitmap_pix(root + "/assets/bitmaps/text.bmp")

        self.compare_arrays("text", canvas_pix, bmp_pix)

    def test_multiline_text(self):
        self.miniscreen.reset()
        canvas_pix = self.miniscreen.core.canvas.multiline_text(
            self.miniscreen.core.canvas.top_left(), "Hello World!")
        bmp_pix = self.get_bitmap_pix(
            root + "/assets/bitmaps/multiline_text.bmp")

        self.compare_arrays("multiline_text", canvas_pix, bmp_pix)

    def test_max_fps(self):
        max_fps = 50
        self.miniscreen.reset()
        self.miniscreen.fps_regulator.set_max_fps(max_fps)
        max_sleep_time = self.miniscreen.fps_regulator.max_sleep_time
        self.assertEqual(max_sleep_time, 1 / max_fps)
