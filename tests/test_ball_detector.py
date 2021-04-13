from sys import modules
from unittest.mock import Mock


modules_to_patch = [
    "PIL",
    "luma.core.interface.serial",
    "luma.oled.device",
    "pyinotify",
    "pitop.camera",
    "numpy",
    "simple_pid",
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
    modules[module] = Mock()


from unittest import TestCase
from pitop.processing.algorithms.ball_detect import BallDetector
from pitop.core.ImageFunctions import convert
from pitop.processing.utils.vision_functions import (
    import_opencv,
    center_reposition,
)


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]

import numpy as np
from PIL import Image

colour = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0)
}


class TestBallDetector(TestCase):

    def __init__(self):
        super(TestCase, self).__init__()
        self.cv2 = import_opencv()
        self._height = 480
        self._width = 640
        self._MAX_DIMENSION_DIFFERENCE = 3
        self._blank_cv_frame = np.zeros((self._height, self._width, 3), np.uint8)

    def test_detect_one_ball(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 80

        red_ball_center = (self._width // 4, self._height // 2)
        self.cv2.circle(cv_frame, red_ball_center, ball_radius, colour['red'], -1)
        red_ball_center = center_reposition(red_ball_center, cv_frame)

        pil_frame = convert(cv_frame, "PIL")

        balls = ball_detector.detect(pil_frame, colour="red")

        red_ball = balls.red

        # Check found boolean
        self.assertTrue(red_ball.found)

        # Check ball centers
        for u, v in zip(red_ball.center, red_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check ball radii
        self.assertAlmostEqual(red_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check PIL image is returned
        self.assertIsInstance(balls.robot_view, Image.Image)

    def test_detect_all_balls(self):
        ball_detector = BallDetector()

        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 80

        red_ball_center = (self._width // 4, self._height // 2)
        self.cv2.circle(cv_frame, red_ball_center, ball_radius, colour['red'], -1)
        red_ball_center = center_reposition(red_ball_center, cv_frame)

        green_ball_center = (self._width // 2, self._height // 2)
        self.cv2.circle(cv_frame, green_ball_center, ball_radius, colour['green'], -1)
        green_ball_center = center_reposition(green_ball_center, cv_frame)

        blue_ball_center = (3 * self._width // 4, self._height // 2)
        self.cv2.circle(cv_frame, blue_ball_center, ball_radius, colour['blue'], -1)
        blue_ball_center = center_reposition(blue_ball_center, cv_frame)

        pil_frame = convert(cv_frame, "PIL")

        balls = ball_detector.detect(pil_frame, colour=("red", "green", "blue"))

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check found boolean
        self.assertTrue(red_ball.found)
        self.assertTrue(green_ball.found)
        self.assertTrue(blue_ball.found)

        # Check ball centers
        for u, v in zip(red_ball.center, red_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)
        for u, v in zip(green_ball.center, green_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)
        for u, v in zip(blue_ball.center, blue_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check ball radii
        self.assertAlmostEqual(red_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE)
        self.assertAlmostEqual(green_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE)
        self.assertAlmostEqual(blue_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check PIL image is returned
        self.assertIsInstance(balls.robot_view, Image.Image)

    def test_detect_no_balls(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()
        pil_frame = convert(cv_frame, "PIL")
        balls = ball_detector.detect(pil_frame, colour=("red", "green", "blue"))

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check found boolean
        self.assertFalse(red_ball.found)
        self.assertFalse(green_ball.found)
        self.assertFalse(blue_ball.found)

        # Check ball centers
        self.assertIsNone(red_ball.center)
        self.assertIsNone(green_ball.center)
        self.assertIsNone(blue_ball.center)

        # Check ball radii
        self.assertIsNone(red_ball.radius)
        self.assertIsNone(green_ball.radius)
        self.assertIsNone(blue_ball.radius)

        # Check PIL image is returned
        self.assertIsInstance(balls.robot_view, Image.Image)


if __name__ == "__main__":
    TestBallDetector().test_detect_one_ball()
    TestBallDetector().test_detect_all_balls()
    TestBallDetector().test_detect_no_balls()
