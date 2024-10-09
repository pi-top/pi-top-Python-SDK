import cv2
import numpy as np
import pytest

from pitop.core.ImageFunctions import convert
from pitop.processing.algorithms.ball_detect import BallDetector
from pitop.processing.core.vision_functions import (
    center_reposition,
    get_object_target_lock_control_angle,
)

color = {"red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0)}


_height = 480
_width = 640
_MAX_DIMENSION_DIFFERENCE = 3
_blank_cv_frame = np.zeros((_height, _width, 3), np.uint8)


def test_detect_one_ball():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()

    ball_radius = 80

    red_ball_center = (_width // 4, _height // 2)
    cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)
    red_ball_center = center_reposition(red_ball_center, cv_frame)
    red_ball_angle = get_object_target_lock_control_angle(red_ball_center, cv_frame)

    balls = ball_detector(cv_frame, color="red")

    red_ball = balls.red

    # Check found boolean
    assert red_ball.found is True

    # Check ball centers
    for u, v in zip(red_ball.center, red_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE

    # Check ball radii
    assert abs(red_ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE

    # Check angle
    assert abs(red_ball.angle - red_ball_angle) <= _MAX_DIMENSION_DIFFERENCE

    # Check center points deque has been appended
    assert len(red_ball.center_points) == 1

    # Check OpenCV image is returned
    assert isinstance(balls.robot_view, np.ndarray)


def test_detection_with_new_hsv_color():
    ball_detector = BallDetector()
    ball_detector.add_color(
        color="yellowish", hsv={"lower": (21, 100, 100), "upper": (36, 255, 255)}
    )

    cv_frame = _blank_cv_frame.copy()

    # Draw yellow ball on frame
    ball_radius = 80
    yellow_ball_center = (_width // 2, _height // 2)
    cv2.circle(cv_frame, yellow_ball_center, ball_radius, (0, 255, 255), -1)
    yellow_ball_center = center_reposition(yellow_ball_center, cv_frame)
    yellow_ball_angle = get_object_target_lock_control_angle(
        yellow_ball_center, cv_frame
    )

    pil_frame = convert(cv_frame, "PIL")

    balls = ball_detector(pil_frame, color=["yellowish"])
    ball = balls.yellowish

    # Check found boolean
    assert ball.found is True

    # Check ball centers
    for u, v in zip(ball.center, yellow_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE

    # Check ball radii
    assert abs(ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE

    # Check angle
    assert abs(ball.angle - yellow_ball_angle) <= _MAX_DIMENSION_DIFFERENCE

    # Check only one center point has been appended to deque
    assert len(ball.center_points) == 1

    # Check OpenCV image is returned
    assert isinstance(balls.robot_view, np.ndarray)

    # Check that a second false detection attempt still returns a longer deque
    cv_frame = _blank_cv_frame.copy()
    pil_frame = convert(cv_frame, "PIL")
    balls = ball_detector(pil_frame, color=["yellowish"])

    ball = balls.yellowish

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(ball.center_points) == 2


def test_detection_with_custom_hsv_color():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()

    # Draw yellow ball on frame
    ball_radius = 80
    yellow_ball_center = (_width // 2, _height // 2)
    cv2.circle(cv_frame, yellow_ball_center, ball_radius, (0, 255, 255), -1)
    yellow_ball_center = center_reposition(yellow_ball_center, cv_frame)
    yellow_ball_angle = get_object_target_lock_control_angle(
        yellow_ball_center, cv_frame
    )

    pil_frame = convert(cv_frame, "PIL")

    balls = ball_detector(pil_frame, hsv_limits=[(23, 100, 100), (31, 255, 255)])

    # a ball with a custom color was found
    assert len(balls.found.keys()) == 1
    assert "color_" in list(balls.found.keys())[0]
    assigned_color_name = list(balls.found.keys())[0]
    ball = balls[assigned_color_name]

    # Check found boolean
    assert ball.found is True

    # Check ball centers
    for u, v in zip(ball.center, yellow_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE

    # Check ball radii
    assert abs(ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE

    # Check angle
    assert abs(ball.angle - yellow_ball_angle) <= _MAX_DIMENSION_DIFFERENCE

    # Check only one center point has been appended to deque
    assert len(ball.center_points) == 1

    # Check OpenCV image is returned
    assert isinstance(balls.robot_view, np.ndarray)

    # Check that a second false detection attempt still returns a longer deque
    cv_frame = _blank_cv_frame.copy()
    pil_frame = convert(cv_frame, "PIL")
    balls = ball_detector(pil_frame, color=assigned_color_name)

    # assigned color was reused
    assert len(balls.found.keys()) == 1
    assert assigned_color_name == list(balls.found.keys())[0]

    ball = balls[assigned_color_name]

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(ball.center_points) == 2

    # Check again using the same hsv limits - should reuse the same color name as before
    balls = ball_detector(pil_frame, hsv_limits=[(23, 100, 100), (31, 255, 255)])

    # assigned color was reused
    assert len(balls.found.keys()) == 1
    assert assigned_color_name == list(balls.found.keys())[0]

    ball = balls[assigned_color_name]

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(ball.center_points) == 3


def test_detect_all_balls():
    ball_detector = BallDetector()

    cv_frame = _blank_cv_frame.copy()

    ball_radius = 80

    red_ball_center = (_width // 4, _height // 2)
    cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)
    red_ball_center = center_reposition(red_ball_center, cv_frame)
    red_ball_angle = get_object_target_lock_control_angle(red_ball_center, cv_frame)

    green_ball_center = (_width // 2, _height // 2)
    cv2.circle(cv_frame, green_ball_center, ball_radius, color["green"], -1)
    green_ball_center = center_reposition(green_ball_center, cv_frame)
    green_ball_angle = get_object_target_lock_control_angle(green_ball_center, cv_frame)

    blue_ball_center = (3 * _width // 4, _height // 2)
    cv2.circle(cv_frame, blue_ball_center, ball_radius, color["blue"], -1)
    blue_ball_center = center_reposition(blue_ball_center, cv_frame)
    blue_ball_angle = get_object_target_lock_control_angle(blue_ball_center, cv_frame)

    # insert random colour artifacts to ensure center points deque does not get incremented by them
    red_artifact_center = (_width // 4, 0)
    cv2.circle(cv_frame, red_artifact_center, 20, color["blue"], -1)
    green_artifact_center = (_width // 2, 0)
    cv2.circle(cv_frame, green_artifact_center, 20, color["blue"], -1)
    blue_artifact_center = (3 * _width // 4, 0)
    cv2.circle(cv_frame, blue_artifact_center, 20, color["blue"], -1)

    pil_frame = convert(cv_frame, "PIL")

    balls = ball_detector(pil_frame, color=["red", "green", "blue"])

    red_ball = balls.red
    green_ball = balls.green
    blue_ball = balls.blue

    # Check found boolean
    assert red_ball.found is True
    assert green_ball.found is True
    assert blue_ball.found is True

    # Check ball centers
    for u, v in zip(red_ball.center, red_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE
    for u, v in zip(green_ball.center, green_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE
    for u, v in zip(blue_ball.center, blue_ball_center):
        assert abs(u - v) <= _MAX_DIMENSION_DIFFERENCE

    # Check ball radii
    assert abs(red_ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE
    assert abs(green_ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE
    assert abs(blue_ball.radius - ball_radius) <= _MAX_DIMENSION_DIFFERENCE

    # Check angle
    assert abs(red_ball.angle - red_ball_angle) <= _MAX_DIMENSION_DIFFERENCE
    assert abs(green_ball.angle - green_ball_angle) <= _MAX_DIMENSION_DIFFERENCE
    assert abs(blue_ball.angle - blue_ball_angle) <= _MAX_DIMENSION_DIFFERENCE

    # Check only one center point has been appended to deque
    assert len(red_ball.center_points) == 1
    assert len(green_ball.center_points) == 1
    assert len(blue_ball.center_points) == 1

    # Check OpenCV image is returned
    assert isinstance(balls.robot_view, np.ndarray)

    # Check that a second false detection attempt still returns a longer deque
    cv_frame = _blank_cv_frame.copy()
    pil_frame = convert(cv_frame, "PIL")
    balls = ball_detector(pil_frame, color=["red", "green", "blue"])

    red_ball = balls.red
    green_ball = balls.green
    blue_ball = balls.blue

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(red_ball.center_points) == 2
    assert len(green_ball.center_points) == 2
    assert len(blue_ball.center_points) == 2


def test_detect_no_balls():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()
    pil_frame = convert(cv_frame, "PIL")
    balls = ball_detector(pil_frame, color=["red", "green", "blue"])

    red_ball = balls.red
    green_ball = balls.green
    blue_ball = balls.blue

    # Check found boolean
    assert red_ball.found is False
    assert green_ball.found is False
    assert blue_ball.found is False
    assert blue_ball.found is False

    # Check ball centers
    assert red_ball.center is None
    assert green_ball.center is None
    assert blue_ball.center is None

    # Check ball radius
    assert red_ball.radius == 0
    assert green_ball.radius == 0
    assert blue_ball.radius == 0

    # Check ball centers
    assert red_ball.angle is None
    assert green_ball.angle is None
    assert blue_ball.angle is None

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(red_ball.center_points) == 1
    assert len(green_ball.center_points) == 1
    assert len(blue_ball.center_points) == 1

    # Check OpenCV image is returned
    assert isinstance(balls.robot_view, np.ndarray)

    # Check that another detection attempt returns a longer deque
    balls = ball_detector(pil_frame, color=["red", "green", "blue"])

    red_ball = balls.red
    green_ball = balls.green
    blue_ball = balls.blue

    # Check center points deque has been appended (even None should get appended if no ball detected)
    assert len(red_ball.center_points) == 2
    assert len(green_ball.center_points) == 2
    assert len(blue_ball.center_points) == 2


def test_detect_close_ball_occluded():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()

    ball_radius = _width // 2

    red_ball_center = (_width // 2, _height)
    cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)

    balls = ball_detector(cv_frame, color="red")
    red_ball = balls.red

    # Check found boolean
    assert red_ball.found is True


def test_small_circle_not_detected():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()

    ball_radius = 9

    red_ball_center = (_width // 2, _height // 2)
    cv2.circle(cv_frame, red_ball_center, ball_radius, color["red"], -1)

    balls = ball_detector(cv_frame, color="red")
    red_ball = balls.red

    assert red_ball.found is False
    assert red_ball.center is None
    assert red_ball.radius == 0
    assert red_ball.angle is None


def test_wrong_color_values():
    ball_detector = BallDetector()
    cv_frame = _blank_cv_frame.copy()
    pil_frame = convert(cv_frame, "PIL")

    for color in (
        "rainbow",
        ["rainbow", "red"],
        [0, 1],
    ):
        with pytest.raises(ValueError):
            ball_detector(pil_frame, color)
