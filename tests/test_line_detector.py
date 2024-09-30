import cv2
import numpy as np
import PIL

from pitop.processing.algorithms.line_detect import process_frame_for_line

_height = 480
_width = 640
_blank_cv_frame = np.zeros((_height, _width, 3), np.uint8)

bgr = {
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
}

hsv = {
    # color: (lower limit, higher limit)
    "red": ((0, 100, 100), (10, 255, 255)),
    "green": ((60, 100, 100), (90, 255, 255)),
    "blue": ((100, 100, 100), (130, 255, 255)),
}


def test_detect_lines_multiple_colors_by_hsv_limits():
    # detect lines of different colors by specifying the HSV limits
    for color_str in bgr:
        cv_frame = _blank_cv_frame.copy()

        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            hsv_limits=hsv[color_str],
        )

        # Empty image, line detection should return None
        assert processed_frame.line_center is None
        assert processed_frame.rectangle_dimensions is None
        assert processed_frame.angle is None
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)

        # Drawing a vertical line on the image
        cv2.line(cv_frame, (_width // 2, 0), (_width // 2, _height), bgr[color_str], 15)
        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            hsv_limits=hsv[color_str],
        )

        # line should be detected
        assert processed_frame.line_center == (-1, 1)
        assert processed_frame.rectangle_dimensions is not None
        assert processed_frame.angle == -0.2
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)

        # If image contains multiple lines
        cv2.line(cv_frame, (_width // 3, 0), (_width // 3, _height), bgr[color_str], 25)
        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            hsv_limits=hsv[color_str],
        )

        # Line center is moved to the left due to the new line being larger
        assert processed_frame.line_center == (-55, 1)
        assert processed_frame.rectangle_dimensions is not None
        assert abs(processed_frame.angle) - 9.5 < 1
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)


def test_detect_lines_multiple_colors_by_color_name():
    # detect lines of different colors by specifying the color name
    for color_str in bgr:
        print(f"Testing color: {color_str}")
        cv_frame = _blank_cv_frame.copy()

        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            color=color_str,
        )

        # Empty image, line detection should return None
        assert processed_frame.line_center is None
        assert processed_frame.rectangle_dimensions is None
        assert processed_frame.angle is None
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)

        # Drawing a vertical line on the image
        cv2.line(cv_frame, (_width // 2, 0), (_width // 2, _height), bgr[color_str], 15)
        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            color=color_str,
        )
        print(processed_frame)

        # line should be detected
        assert processed_frame.line_center == (-1, 1)
        assert processed_frame.rectangle_dimensions is not None
        assert processed_frame.angle == -0.2
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)

        # If image contains multiple lines
        cv2.line(cv_frame, (_width // 3, 0), (_width // 3, _height), bgr[color_str], 25)
        processed_frame = process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            color=color_str,
        )

        # Line center is moved to the left due to the new line being larger
        assert processed_frame.line_center == (-55, 1)
        assert processed_frame.rectangle_dimensions is not None
        assert abs(processed_frame.angle) - 9.5 < 1
        assert isinstance(processed_frame.robot_view, PIL.Image.Image)


def test_line_detection_using_invalid_color_name():
    # when using an invalid color name, a ValueError should be raised
    cv_frame = _blank_cv_frame.copy()

    try:
        process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            color="invalid_color",
        )
    except ValueError as e:
        assert (
            str(e)
            == "Color 'invalid_color' is not supported. You can use one of '['red', 'green', 'blue', 'yellow']' or provide your own HSV limits."
        )


def test_line_detection_using_both_color_name_and_hsv_limits():
    # when using both color name and hsv limits, a ValueError should be raised
    cv_frame = _blank_cv_frame.copy()

    try:
        process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            color="red",
            hsv_limits=([0, 100, 100], [10, 255, 255]),
        )
    except ValueError as e:
        assert str(e) == "Cannot specify both color and hsv_limits"


def test_line_detection_using_invalid_hsv_limits():
    # when using invalid hsv limits, a ValueError should be raised
    cv_frame = _blank_cv_frame.copy()

    try:
        process_frame_for_line(
            cv_frame,
            image_format="PIL",
            process_image_width=320,
            hsv_limits="oh oh, this is wrong",
        )
    except AssertionError as e:
        assert str(e) == "hsv_limits must be a tuple of 2 elements"
