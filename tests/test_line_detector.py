import cv2
import numpy as np
import PIL

from pitop.processing.algorithms.line_detect import process_frame_for_line

_height = 480
_width = 640
_MAX_DIMENSION_DIFFERENCE = 3
_blank_cv_frame = np.zeros((_height, _width, 3), np.uint8)


def test_detect_lines_multiple_colors():
    bgr = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
    }

    hsv = {
        # color: (lower, higher)
        "red": ((0, 100, 100), (10, 255, 255)),
        "green": ((60, 100, 100), (90, 255, 255)),
        "blue": ((100, 100, 100), (130, 255, 255)),
    }

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
