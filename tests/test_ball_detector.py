from unittest import TestCase

import cv2
import numpy as np
from pitop.core.ImageFunctions import convert
from pitop.processing.algorithms.ball_detect import BallDetector
from pitop.processing.core.vision_functions import (
    center_reposition,
    get_object_target_lock_control_angle,
)

color = {"red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0)}


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
        cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)
        red_ball_center = center_reposition(red_ball_center, cv_frame)
        red_ball_angle = get_object_target_lock_control_angle(red_ball_center, cv_frame)

        balls = ball_detector(cv_frame, color="red")

        red_ball = balls.red

        # Check found boolean
        self.assertTrue(red_ball.found)

        # Check ball centers
        for u, v in zip(red_ball.center, red_ball_center):
            self.assertAlmostEqual(u, v, delta=self._MAX_DIMENSION_DIFFERENCE)

        # Check ball radii
        self.assertAlmostEqual(
            red_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE
        )

        # Check angle
        self.assertAlmostEqual(
            red_ball.angle, red_ball_angle, delta=self._MAX_DIMENSION_DIFFERENCE
        )

        # Check center points deque has been appended
        self.assertEqual(len(red_ball.center_points), 1)

        # Check OpenCV image is returned
        self.assertIsInstance(balls.robot_view, np.ndarray)

    def test_detect_all_balls(self):
        ball_detector = BallDetector()

        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 80

        red_ball_center = (self._width // 4, self._height // 2)
        cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)
        red_ball_center = center_reposition(red_ball_center, cv_frame)
        red_ball_angle = get_object_target_lock_control_angle(red_ball_center, cv_frame)

        green_ball_center = (self._width // 2, self._height // 2)
        cv2.circle(cv_frame, green_ball_center, ball_radius, color["green"], -1)
        green_ball_center = center_reposition(green_ball_center, cv_frame)
        green_ball_angle = get_object_target_lock_control_angle(
            green_ball_center, cv_frame
        )

        blue_ball_center = (3 * self._width // 4, self._height // 2)
        cv2.circle(cv_frame, blue_ball_center, ball_radius, color["blue"], -1)
        blue_ball_center = center_reposition(blue_ball_center, cv_frame)
        blue_ball_angle = get_object_target_lock_control_angle(
            blue_ball_center, cv_frame
        )

        # insert random colour artifacts to ensure center points deque does not get incremented by them
        red_artifact_center = (self._width // 4, 0)
        cv2.circle(cv_frame, red_artifact_center, 20, color["blue"], -1)
        green_artifact_center = (self._width // 2, 0)
        cv2.circle(cv_frame, green_artifact_center, 20, color["blue"], -1)
        blue_artifact_center = (3 * self._width // 4, 0)
        cv2.circle(cv_frame, blue_artifact_center, 20, color["blue"], -1)

        pil_frame = convert(cv_frame, "PIL")

        balls = ball_detector(pil_frame, color=["red", "green", "blue"])

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
        self.assertAlmostEqual(
            red_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE
        )
        self.assertAlmostEqual(
            green_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE
        )
        self.assertAlmostEqual(
            blue_ball.radius, ball_radius, delta=self._MAX_DIMENSION_DIFFERENCE
        )

        # Check angle
        self.assertAlmostEqual(
            red_ball.angle, red_ball_angle, delta=self._MAX_DIMENSION_DIFFERENCE
        )
        self.assertAlmostEqual(
            green_ball.angle, green_ball_angle, delta=self._MAX_DIMENSION_DIFFERENCE
        )
        self.assertAlmostEqual(
            blue_ball.angle, blue_ball_angle, delta=self._MAX_DIMENSION_DIFFERENCE
        )

        # Check only one center point has been appended to deque
        self.assertEqual(len(red_ball.center_points), 1)
        self.assertEqual(len(green_ball.center_points), 1)
        self.assertEqual(len(blue_ball.center_points), 1)

        # Check OpenCV image is returned
        self.assertIsInstance(balls.robot_view, np.ndarray)

        # Check that a second false detection attempt still returns a longer deque
        cv_frame = self._blank_cv_frame.copy()
        pil_frame = convert(cv_frame, "PIL")
        balls = ball_detector(pil_frame, color=["red", "green", "blue"])

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check center points deque has been appended (even None should get appended if no ball detected)
        self.assertEqual(len(red_ball.center_points), 2)
        self.assertEqual(len(green_ball.center_points), 2)
        self.assertEqual(len(blue_ball.center_points), 2)

    def test_detect_no_balls(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()
        pil_frame = convert(cv_frame, "PIL")
        balls = ball_detector(pil_frame, color=["red", "green", "blue"])

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check found boolean
        self.assertFalse(red_ball.found)
        self.assertFalse(green_ball.found)
        self.assertFalse(blue_ball.found)
        self.assertFalse(blue_ball.found)

        # Check ball centers
        self.assertIsNone(red_ball.center)
        self.assertIsNone(green_ball.center)
        self.assertIsNone(blue_ball.center)

        # Check ball radius
        self.assertEqual(red_ball.radius, 0)
        self.assertEqual(green_ball.radius, 0)
        self.assertEqual(blue_ball.radius, 0)

        # Check ball centers
        self.assertIsNone(red_ball.angle)
        self.assertIsNone(green_ball.angle)
        self.assertIsNone(blue_ball.angle)

        # Check center points deque has been appended (even None should get appended if no ball detected)
        self.assertEqual(len(red_ball.center_points), 1)
        self.assertEqual(len(green_ball.center_points), 1)
        self.assertEqual(len(blue_ball.center_points), 1)

        # Check OpenCV image is returned
        self.assertIsInstance(balls.robot_view, np.ndarray)

        # Check that another detection attempt returns a longer deque
        balls = ball_detector(pil_frame, color=["red", "green", "blue"])

        red_ball = balls.red
        green_ball = balls.green
        blue_ball = balls.blue

        # Check center points deque has been appended (even None should get appended if no ball detected)
        self.assertEqual(len(red_ball.center_points), 2)
        self.assertEqual(len(green_ball.center_points), 2)
        self.assertEqual(len(blue_ball.center_points), 2)

    def test_detect_close_ball_occluded(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()

        ball_radius = self._width // 2

        red_ball_center = (self._width // 2, self._height)
        cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)

        balls = ball_detector(cv_frame, color="red")
        red_ball = balls.red

        # Check found boolean
        self.assertTrue(red_ball.found)

    def test_small_circle_not_detected(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()

        ball_radius = 9

        red_ball_center = (self._width // 2, self._height // 2)
        cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)

        balls = ball_detector(cv_frame, color="red")
        red_ball = balls.red

        self.assertFalse(red_ball.found)
        self.assertIsNone(red_ball.center)
        self.assertEqual(red_ball.radius, 0)
        self.assertIsNone(red_ball.angle)

    def test_wrong_color_values(self):
        ball_detector = BallDetector()
        cv_frame = self._blank_cv_frame.copy()
        pil_frame = convert(cv_frame, "PIL")
        self.assertRaises(ValueError, ball_detector, pil_frame, color="rainbow")
        self.assertRaises(
            ValueError, ball_detector, pil_frame, color=["rainbow", "red"]
        )
        self.assertRaises(ValueError, ball_detector, pil_frame, color=[0, 1])


if __name__ == "__main__":
    test_ball_detector = TestBallDetector()
    test_ball_detector.setUp()
    test_ball_detector.test_detect_one_ball()
    test_ball_detector.test_detect_all_balls()
    test_ball_detector.test_detect_no_balls()
    test_ball_detector.test_wrong_color_values()
    test_ball_detector.test_detect_close_ball_occluded()
    test_ball_detector.test_small_circle_not_detected()
