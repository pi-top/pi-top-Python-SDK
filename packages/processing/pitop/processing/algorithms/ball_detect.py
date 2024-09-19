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


class HSVColorRanges:
    ranges = {
        "red": [
            {"lower": (150, 100, 100), "upper": (179, 255, 255)},
            {"lower": (0, 100, 100), "upper": (5, 255, 255)},
        ],
        "green": [{"lower": (60, 100, 100), "upper": (90, 255, 255)}],
        "blue": [{"lower": (100, 100, 100), "upper": (130, 255, 255)}],
    }

    @classmethod
    def supported(cls):
        return list(cls.ranges.keys())

    @classmethod
    def get(cls, color: str) -> list:
        return cls.ranges[color]

    @classmethod
    def add(cls, color: str, lower: tuple, upper: tuple):
        if not all(isinstance(i, tuple) for i in (lower, upper)):
            raise ValueError("Lower and upper must be tuples")

        if color not in cls.ranges:
            cls.ranges[color] = []
        cls.ranges[color].append({"lower": lower, "upper": upper})

    @classmethod
    def validate(cls, color_arg: Union[str, list]) -> list:
        colors = []
        supported_colors = cls.supported()
        if isinstance(color_arg, str):
            colors = [color_arg]
        elif type(color_arg) in (list, tuple):
            colors = color_arg
        if not set(colors).issubset(supported_colors):
            raise ValueError(
                f"Valid color values are {', '.join(supported_colors[:-1])} or {supported_colors[-1]}"
            )
        return colors


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
    """Representation of a ball.

    Attributes:
        color: Color of the ball
        angle: Angle between the approximate robot chassis center and the ball in the frame. Used for input to a PID
        algorithm to align a robot chassis with the ball center (drive in a direction that keeps the ball in the middle
        of the frame)
        center: (x, y) coordinates of the ball where (0, 0) is the middle of the image frame used to detect it.
        radius: Radius of the detected ball in pixels in relation to the image frame used to detect it.
        center_points: deque of (x, y) coordinates for historical ball detections where (0, 0) is the top left of the frame.
    """

    MIN_RADIUS = 5
    CLOSE_RADIUS = 50

    # 'Holding a red ball' can produce issues
    # since some skin types are redish in color
    minimum_shape_accuracies = {"red": 0.1, "green": 0.05, "blue": 0.05}

    def __init__(self, color):
        self.color = color
        self.minimum_shape_accuracy = self.minimum_shape_accuracies.get(color, 0.1)

        self.center_points = deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH)
        self.center = None
        self.radius = 0
        self.angle = None

    @property
    def found(self) -> bool:
        # Deprecated in favor of 'valid' property
        return self.valid

    @property
    def valid(self) -> bool:
        """
        :return: Boolean to determine if a ball exists
        :rtype: bool
        """
        return self.center is not None

    def draw_position(self, frame):
        if len(self.center_points) == 0 or self.center_points[0] is None:
            return
        cv2.circle(frame, self.center_points[0], self.radius, (0, 255, 255), 2)
        cv2.circle(
            frame,
            self.center_points[0],
            5,
            tuple_for_color_by_name(self.color, bgr=True),
            -1,
        )

    def draw_contrail(self, frame):
        for i in range(1, len(self.center_points)):
            if self.center_points[i - 1] is None or self.center_points[i] is None:
                continue
            thickness = int(np.sqrt(DETECTION_POINTS_BUFFER_LENGTH / float(i + 1)))

            cv2.line(
                frame,
                self.center_points[i - 1],
                self.center_points[i],
                tuple_for_color_by_name(self.color, bgr=True),
                thickness,
            )


class SingleBallDetector:
    def __init__(self, color: str, image_processing_width: int):
        self.color = color
        self.ball = Ball(color)
        self._image_processing_width = image_processing_width
        self._frame_scaler = None

    def draw(self, frame):
        """Draws the ball on top of the given frame."""
        frame = ImageFunctions.convert(frame, "OpenCV")
        self.ball.draw_contrail(frame)
        if self.found:
            self.ball.draw_position(frame)
        return frame

    def found(self) -> bool:
        """
        :return: Boolean to determine if a valid ball was found in the frame.
        :rtype: bool
        """
        return self.ball.valid

    def will_accept(self, ball: Ball, ball_likeness: BallLikeness):
        """Check if the ball will accept the new ball likeness based on the
        radius and shape accuracy."""
        if ball_likeness.radius < ball.MIN_RADIUS:
            return False

        if ball_likeness.circular_likeness < ball.minimum_shape_accuracy:
            return True

        if ball_likeness.radius > ball.CLOSE_RADIUS:
            return True

        return False

    def _do_find(self, frame) -> Ball:
        """Finds a ball in a frame."""
        contours = find_contours(frame, self.color)
        ball = self.ball

        # Reset ball state
        ball.center = None
        ball.radius = 0
        ball.angle = None

        if len(contours) == 0:
            # No ball found
            ball.center_points.appendleft(None)
            return ball

        highest_likelihood = 0

        # Check each contour for ball likeness
        for contour in contours:
            ball_likeness = BallLikeness(contour)

            if ball_likeness.likelihood < highest_likelihood:
                continue

            # Don't accept future balls which are less likely
            highest_likelihood = ball_likeness.likelihood
            if self.will_accept(ball, ball_likeness):
                ball.center = ball_likeness.pos
                ball.radius = ball_likeness.radius

        return ball

    def find(self, frame) -> Ball:
        """Finds a ball in a frame.

        Scales down the provided frame to reduce processing time.
        """

        # Scale image
        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = width / self._image_processing_width

        # Find ball in frame
        ball = self._do_find(
            frame=imutils.resize(frame, width=self._image_processing_width)
        )

        # If a valid ball was found, scale the center and radius back to the original frame size
        if ball.valid:
            new_center = tuple(
                int(coordinate * self._frame_scaler) for coordinate in ball.center
            )

            # Update ball state
            ball.center_points.appendleft(new_center)
            ball.center = center_reposition(new_center, frame)
            ball.angle = get_object_target_lock_control_angle(ball.center, frame)
            ball.radius = int(ball.radius * self._frame_scaler)

        self.ball = ball
        return self.ball


class BallDetector:
    def __init__(self, image_processing_width: int = 320, format: str = "OpenCV"):
        """
        :param int image_processing_width: image width to scale to for image processing
        :param str format: output image format
        """
        import_libs()
        self.image_processing_width = image_processing_width
        self.format = format
        self.detectors = {}

        # Enable FPS if environment variable is set
        self._print_fps = getenv("PT_ENABLE_FPS", "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self._print_fps)

    @property
    def balls(self):
        return {c: self.detectors[c].ball for c in self.detectors}

    def add_color_hsv(self, color: str, lower: tuple, upper: tuple):
        HSVColorRanges.add(color, lower, upper)
        self.detectors[color] = SingleBallDetector(color, self.image_processing_width)

    def _print_fps(self):
        self._fps.stop()

    def __call__(self, frame, color: Union[str, list] = "red"):
        frame = ImageFunctions.convert(frame, format="OpenCV")
        robot_view = frame.copy()
        data = DotDict({})

        for c in HSVColorRanges.validate(color):
            # Find or create detector for given color if it doesn't exist
            if c not in self.detectors:
                self.detectors[c] = SingleBallDetector(c, self.image_processing_width)
            detector = self.detectors[c]

            # Find ball in frame
            data[c] = detector.find(frame)

            # Draw ball on top of frame
            robot_view = detector.draw(robot_view)
        data["robot_view"] = ImageFunctions.convert(robot_view, self.format)

        if self._print_fps:
            self._fps.update()

        return data


def get_color_mask(frame, color: str):
    blurred = cv2.blur(frame, (11, 11))
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    masks = []
    for color_range in HSVColorRanges.get(color):
        mask = cv2.inRange(hsv, color_range["lower"], color_range["upper"])
        masks.append(mask)
    mask = sum(masks)

    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)

    return mask


def find_contours(frame, color: str):
    mask = get_color_mask(frame, color=color)

    return imutils.grab_contours(  # fixes problems with OpenCV changing their protocol
        cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    )
