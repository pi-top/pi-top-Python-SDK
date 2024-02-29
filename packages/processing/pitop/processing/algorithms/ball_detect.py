import atexit
from collections import deque
from os import getenv
from typing import Union

import numpy as np
from imutils.video import FPS

from pitop.core import ImageFunctions
from pitop.core.data_structures import DotDict
from pitop.processing.core.vision_functions import (
    center_reposition,
    get_object_target_lock_control_angle,
    import_imutils,
    import_opencv,
    tuple_for_color_by_name,
)

VALID_COLORS = ["red", "green", "blue"]
DETECTION_POINTS_BUFFER_LENGTH = 16

cv2 = None
imutils = None


def import_libs():
    global cv2, imutils
    if cv2 is None:
        cv2 = import_opencv()
    if imutils is None:
        imutils = import_imutils()


class BallLikeness:
    def __init__(self, contour):
        import_libs()

        self.contour = contour
        self.pos, self.radius = cv2.minEnclosingCircle(self.contour)
        self.area = cv2.contourArea(self.contour)

        self.circular_likeness = cv2.matchShapes(
            self.contour, self.__circular_match_contour(), 1, 0.0
        )

        # Most likely ball is a mixture of largest area and one that is most "ball-shaped"
        self.likelihood = self.area / (self.circular_likeness + 1e-5)

    def __circular_match_contour(self):
        # Initialise empty mask
        mask_to_compare = np.zeros(
            (int(2 * self.radius), int(2 * self.radius)), dtype="uint8"
        )

        # Draw circle matching contour's position and radius
        cv2.circle(
            mask_to_compare,
            (int(self.radius), int(self.radius)),
            int(self.radius),
            255,
            -1,
        )

        return max(
            imutils.grab_contours(
                cv2.findContours(
                    mask_to_compare, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
            ),
            key=cv2.contourArea,
        )


class Ball:
    MIN_BALL_RADIUS = 5
    BALL_CLOSE_RADIUS = 50

    def __init__(self, color):
        self.color = color

        # 'Holding a red ball' can produce issues
        # since some skin types are redish in color
        minimum_shape_accuracies = {"red": 0.1, "green": 0.05, "blue": 0.05}
        self.minimum_shape_accuracy = minimum_shape_accuracies[color]

        self._center_points = deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH)
        self._center = None
        self._radius = 0
        self._angle = None

    @property
    def angle(self) -> float:
        """
        :return: Angle between the approximate robot chassis center and the ball in the frame. Used for input to a PID
        algorithm to align a robot chassis with the ball center (drive in a direction that keeps the ball in the middle
        of the frame).
        :rtype: float
        """
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value

    @property
    def center(self) -> tuple:
        """
        :return: (x, y) coordinates of the ball where (0, 0) is the middle of the image frame used to detect it.
        :rtype: tuple
        """
        return self._center

    @center.setter
    def center(self, value: tuple):
        self._center = value

    @property
    def radius(self) -> int:
        """
        :return: Radius of the detected ball in pixels in relation to the image frame used to detect it.
        :rtype: int
        """
        return self._radius

    @radius.setter
    def radius(self, value: int):
        self._radius = value

    @property
    def center_points(self) -> deque:
        """
        :return: deque of (x, y) coordinates for historical ball detections where (0, 0) is the top left of the frame.
        :rtype: deque
        """
        return self._center_points

    @property
    def found(self) -> bool:
        """
        :return: Boolean to determine if a valid ball was found in the frame.
        :rtype: bool
        """
        return self.center is not None

    def will_accept(self, ball_likeness: BallLikeness):
        if ball_likeness.radius < self.MIN_BALL_RADIUS:
            return False

        if ball_likeness.circular_likeness < self.minimum_shape_accuracy:
            return True

        if ball_likeness.radius > self.BALL_CLOSE_RADIUS:
            return True

        return False


class BallDetector:
    def __init__(self, image_processing_width: int = 320, format: str = "OpenCV"):
        """
        :param int image_processing_width: image width to scale to for image processing
        :param str format: output image format
        """
        import_libs()

        self._image_processing_width = image_processing_width
        self.format = format
        self.balls = {c: Ball(c) for c in VALID_COLORS}
        self._frame_scaler = None

        # Enable FPS if environment variable is set
        self._print_fps = getenv("PT_ENABLE_FPS", "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def __call__(self, frame, color: Union[str, list] = "red"):
        def parse_colors(color_arg):
            colors = []
            if isinstance(color_arg, str):
                if color_arg not in VALID_COLORS:
                    raise ValueError(
                        f"Valid color values are {', '.join(VALID_COLORS[:-1])} or {VALID_COLORS[-1]}"
                    )
                colors = [color_arg]
            elif type(color_arg) in (list, tuple):
                if not set(color_arg).issubset(VALID_COLORS):
                    raise ValueError(
                        f"Valid color values are {', '.join(VALID_COLORS[:-1])} or {VALID_COLORS[-1]}"
                    )
                colors = color_arg
            if len(colors) > 3:
                raise ValueError("Cannot pass more than three colors.")

            return colors

        import_libs()
        frame = ImageFunctions.convert(frame, format="OpenCV")

        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = width / self._image_processing_width

        for c in parse_colors(color):
            self.balls[c] = self.__find_most_likely_ball(
                ball=self.balls.get(c), frame=frame, color=c
            )

        robot_view = frame.copy()
        ball_data = DotDict({})
        for ball_color, ball_object in self.balls.items():
            ball_data[ball_color] = ball_object
            self.__draw_ball_contrail(robot_view, ball_object)
            if ball_object.found:
                self.__draw_ball_position(robot_view, ball_object)

        ball_data["robot_view"] = ImageFunctions.convert(robot_view, self.format)

        if self._print_fps:
            self._fps.update()

        return ball_data

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")

    def __draw_ball_position(self, frame, ball):
        cv2.circle(frame, ball.center_points[0], ball.radius, (0, 255, 255), 2)
        cv2.circle(
            frame,
            ball.center_points[0],
            5,
            tuple_for_color_by_name(ball.color, bgr=True),
            -1,
        )

    def __draw_ball_contrail(self, frame, ball):
        for i in range(1, len(ball.center_points)):
            if ball.center_points[i - 1] is None or ball.center_points[i] is None:
                continue
            thickness = int(np.sqrt(DETECTION_POINTS_BUFFER_LENGTH / float(i + 1)))

            cv2.line(
                frame,
                ball.center_points[i - 1],
                ball.center_points[i],
                tuple_for_color_by_name(ball.color, bgr=True),
                thickness,
            )

    def color_filter(self, frame, color: str = "red"):
        frame = ImageFunctions.convert(frame, format="OpenCV")
        mask = self.__get_color_mask(frame, color)
        filtered_image = cv2.bitwise_and(frame, frame, mask=mask)
        if self.format.lower() == "pil":
            filtered_image = ImageFunctions.convert(mask, format="PIL")

        return filtered_image

    def __get_color_mask(self, frame, color: str):
        blurred = cv2.blur(frame, (11, 11))
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        masks = []
        color_ranges = {
            "red": [
                {"lower": (150, 100, 100), "upper": (179, 255, 255)},
                {"lower": (0, 100, 100), "upper": (5, 255, 255)},
            ],
            "green": [{"lower": (60, 100, 100), "upper": (90, 255, 255)}],
            "blue": [{"lower": (100, 100, 100), "upper": (130, 255, 255)}],
        }
        for color_range in color_ranges[color]:
            hsv_lower = color_range["lower"]
            hsv_upper = color_range["upper"]
            mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
            masks.append(mask)
        mask = sum(masks)

        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=1)

        return mask

    def __find_contours(self, frame, color):
        mask = self.__get_color_mask(frame, color=color)

        return (
            imutils.grab_contours(  # fixes problems with OpenCV changing their protocol
                cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
            )
        )

    def __find_most_likely_ball(self, ball, frame, color):
        resized_frame = imutils.resize(frame, width=self._image_processing_width)
        contours = self.__find_contours(resized_frame, color)
        if len(contours) == 0:
            ball.center_points.appendleft(None)
            ball.center = None
            ball.radius = 0
            ball.angle = None

            return ball

        highest_likelihood = 0

        ball_center = None
        ball_radius = 0
        for contour in contours:
            ball_likeness = BallLikeness(contour)

            if ball_likeness.likelihood < highest_likelihood:
                continue

            # Don't accept future balls which are less likely
            highest_likelihood = ball_likeness.likelihood
            if ball.will_accept(ball_likeness):
                # Scale to original frame size

                ball_center = tuple(
                    int(coordinate * self._frame_scaler)
                    for coordinate in ball_likeness.pos
                )
                ball_radius = int(ball_likeness.radius * self._frame_scaler)

        # Update ball state
        ball.center_points.appendleft(ball_center)
        ball.center = (
            center_reposition(ball_center, frame) if ball_center is not None else None
        )
        ball.angle = (
            get_object_target_lock_control_angle(ball.center, frame)
            if ball_center is not None
            else None
        )
        ball.radius = ball_radius

        return ball
