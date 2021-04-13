from sys import modules
from unittest.mock import Mock


modules_to_patch = [
    "luma.core.interface.serial",
    "luma.oled.device",
    "pyinotify",
    "pitop.camera",
    "simple_pid",
    "pitopcommon.smbus_device",
    "pitopcommon.logger",
    "pitopcommon.singleton",
    "pitopcommon.common_ids",
    "pitopcommon.current_session_info",
    "pitopcommon.ptdm",
    "pitopcommon.firmware_device",
    "pitopcommon.command_runner",
    "pitopcommon.common_names"

]
for module in modules_to_patch:
    modules[module] = Mock()


from unittest import TestCase
from pitop.processing.algorithms.ball_detect import BallDetector
from pitop.core.ImageFunctions import convert


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]

import numpy as np
import cv2

color = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0)
}


class TestBallDetector(TestCase):

    def setUp(self):
        self._height = 480
        self._width = 640
        self._MAX_DIMENSION_DIFFERENCE = 3
        self._blank_cv_frame = np.zeros((self._height, self._width, 3), np.uint8)

    def test_detect_one_ball(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 80

        red_ball_center = (self._width // 4, self._height // 2)
        cv2.circle(cv_frame, red_ball_center, ball_radius, color['red'], -1)

        balls = ball_detector.detect(cv_frame, color="red")

        red_ball = balls.red

        # Check is_valid() boolean
        self.assertTrue(red_ball.is_valid())

        # Check ball centers
        for u, v in zip(red_ball.center, red_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check ball radii
        self.assertAlmostEqual(red_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check PIL image is returned
        self.assertIsInstance(balls.robot_view, np.ndarray)

    def test_detect_all_balls(self):
        ball_detector = BallDetector()

        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 80

        red_ball_center = (self._width // 4, self._height // 2)
        cv2.circle(cv_frame, red_ball_center, ball_radius, color['red'], -1)

        green_ball_center = (self._width // 2, self._height // 2)
        cv2.circle(cv_frame, green_ball_center, ball_radius, color['green'], -1)

        blue_ball_center = (3 * self._width // 4, self._height // 2)
        cv2.circle(cv_frame, blue_ball_center, ball_radius, color['blue'], -1)

        pil_frame = convert(cv_frame, "PIL")

        balls = ball_detector.detect(pil_frame, color=("red", "green", "blue"))

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check is_valid() boolean
        self.assertTrue(red_ball.is_valid())
        self.assertTrue(green_ball.is_valid())
        self.assertTrue(blue_ball.is_valid())

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
        self.assertIsInstance(balls.robot_view, np.ndarray)

    def test_detect_no_balls(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()
        pil_frame = convert(cv_frame, "PIL")
        balls = ball_detector.detect(pil_frame, color=("red", "green", "blue"))

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check is_valid() boolean
        self.assertFalse(red_ball.is_valid())
        self.assertFalse(green_ball.is_valid())
        self.assertFalse(blue_ball.is_valid())

        # Check ball centers
        self.assertIsNone(red_ball.center)
        self.assertIsNone(green_ball.center)
        self.assertIsNone(blue_ball.center)

        # Check ball radius
        self.assertEquals(red_ball.radius, 0)
        self.assertEquals(green_ball.radius, 0)
        self.assertEquals(blue_ball.radius, 0)

        # Check PIL image is returned
        self.assertIsInstance(balls.robot_view, np.ndarray)


if __name__ == "__main__":
    TestBallDetector().test_detect_one_ball()
    TestBallDetector().test_detect_all_balls()
    TestBallDetector().test_detect_no_balls()
