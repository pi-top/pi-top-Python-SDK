from collections import deque
import numpy as np
from pitop.core import ImageFunctions
from pitop.processing.core.vision_functions import (
    center_reposition,
    get_object_target_lock_control_angle,
)
from typing import Union
from imutils import resize, grab_contours
from imutils.video import FPS
from os import getenv
from pitop.core.data_structures import DotDict
import atexit
from pitop.processing.core.vision_functions import (
    import_opencv,
    tuple_for_color_by_name
)

color_ranges = {
    "red": [
        {
            "lower": (150, 100, 100),
            "upper": (179, 255, 255)
        },
        {
            "lower": (0, 100, 100),
            "upper": (5, 255, 255)
        }
    ],
    "green": [{
        "lower": (60, 100, 100),
        "upper": (90, 255, 255)
    }],
    "blue": [{
        "lower": (100, 100, 100),
        "upper": (130, 255, 255)
    }]
}

MIN_BALL_RADIUS = 5
BALL_CLOSE_RADIUS = 50
DETECTION_POINTS_BUFFER_LENGTH = 64


class Ball:
    def __init__(self, color):
        self.color = color

        # Red needs to be a higher limit
        # since some skin types are redish in color
        match_limits = {
            "red": 0.1,
            "green": 0.05,
            "blue": 0.05
        }
        self.match_limit = match_limits[color]

        self.detection_points = deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH)

        self.center = None
        self.radius = None
        self.angle_from_center = None


class BallDetector:
    def __init__(self,
                 process_image_width: int = 320,
                 format: str = "OpenCV",
                 print_fps: bool = False):
        """
        :param int process_image_width: image width to scale to for image processing
        :param str format: output image format
        """
        self.cv2 = import_opencv()
        self._process_image_width = process_image_width
        self.format = format
        self.balls = {c: None for c in ["red", "green", "blue"]}
        self._frame_scaler = None

        # Enable FPS if environment variable is set
        self._print_fps = getenv("PT_ENABLE_FPS", "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def detect(self, frame, color: Union[str, list] = "red"):
        def parse_colors(color):
            # TODO: return a list of color names (e.g. ["red", "blue"])
            colors = None
            if type(color) == str:
                colors = (color,)
            elif type(color) == list:
                colors = color
            if len(colors) > 3:
                raise ValueError("Cannot pass more than three colors.")

            return colors

        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = width / self._process_image_width

        frame = ImageFunctions.convert(frame, format="OpenCV")

        for c in parse_colors(color):
            ball = self.__find_most_likely_ball(c, frame)

            if ball is not None:
                ball.detection_points.appendleft(ball.center)

            self.balls[c] = ball

        robot_view = frame.copy()
        for ball in self.balls:
            self.__draw_ball_position(robot_view, ball)
            self.__draw_ball_contrail(robot_view, ball)

        robot_view = ImageFunctions.convert(robot_view, self.format)

        ball_data = self.__prepare_return_data(robot_view)

        if self._print_fps:
            self._fps.update()

        return ball_data

    def __prepare_return_data(self, robot_view):
        # TODO: Get this working!
        ball_data = DotDict({})
        ball_data["robot_view"] = robot_view

        for ball in self.balls:
            if ball is None:
                continue

            ball_data[ball.color] = DotDict({
                "center": ball.center,
                "radius": ball.radius,
                "angle": ball.angle
            })

        # if len(colors) == 1:
        #     # if only searching one color, add convenience data so ball_data.data_type can be used directly
        #     color = colors[0]
        #     ball_data["found"] = ball.find
        #     ball_data["center"] = ball.center
        #     ball_data["radius"] = ball.radius
        #     ball_data["angle"] = ball.angle

        return ball_data

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")

    def __draw_ball_position(self, frame, ball):
        self.cv2.circle(frame, ball.center, ball.radius, (0, 255, 255), 2)
        self.cv2.circle(frame, ball.center, 5, tuple_for_color_by_name(ball.color), -1)

    def __draw_ball_contrail(self, frame, ball):
        for i in range(1, len(ball.detection_points)):
            if ball.detection_points[i - 1] is None or ball.detection_points[i] is None:
                continue
            thickness = int(np.sqrt(DETECTION_POINTS_BUFFER_LENGTH / float(i + 1)))

            self.cv2.line(frame, ball.detection_points[i - 1], ball.detection_points[i],
                          tuple_for_color_by_name(ball.color), thickness)

    def color_filter(self,
                     frame,
                     color: str = "red",
                     return_binary_mask: bool = False,
                     format: str = "PIL"
                     ):

        frame = ImageFunctions.convert(frame, format="OpenCV")

        if color.lower() not in ("red", "green", "blue"):
            raise ValueError("Color must be 'red', 'green' or 'blue'")

        blurred = self.cv2.blur(frame, (11, 11))
        hsv = self.cv2.cvtColor(blurred, self.cv2.COLOR_BGR2HSV)

        masks = []
        for color_range in color_ranges[color]:
            hsv_lower = color_range["lower"]
            hsv_upper = color_range["upper"]
            mask = self.cv2.inRange(hsv, hsv_lower, hsv_upper)
            masks.append(mask)
        mask = sum(masks)

        mask = self.cv2.erode(mask, None, iterations=1)
        mask = self.cv2.dilate(mask, None, iterations=1)

        if not return_binary_mask:
            mask = self.cv2.bitwise_and(frame, frame, mask=mask)

        if format.lower() == "pil":
            mask = ImageFunctions.convert(mask, format="PIL")

        return mask

    def __find_contours(self, frame, color):
        mask = self.color_filter(frame, color=color, return_binary_mask=True,
                                 format="OpenCV")

        return grab_contours(  # fixes problems with OpenCV changing their protocol
            self.cv2.findContours(
                mask.copy(),
                self.cv2.RETR_EXTERNAL,
                self.cv2.CHAIN_APPROX_SIMPLE
            )
        )

    def __find_most_likely_ball(self, color, frame):
        resized_frame = resize(frame, width=self._process_image_width)
        contours = self.__find_contours(resized_frame, color)
        if len(contours) == 0:
            return None

        ball = Ball()

        ball.center = None
        ball.radius = None

        max_likelihood_index = 0

        def __meets_minimum_ball_requirements(ball, match_radius, match_value):
            if match_value < ball.match_limit or match_radius > BALL_CLOSE_RADIUS:
                if ball.radius > MIN_BALL_RADIUS:
                    return True
            return False

        for contour in contours:
            (x, y), match_radius = self.cv2.minEnclosingCircle(contour)
            area, match_value = self.__get_ball_likelihood_parameters(resized_frame, contour, x, y, match_radius)

            # most likely ball is a mixture of largest area and one that is most "ball-shaped"
            likelihood_index = area / (match_value + 1e-5)
            if likelihood_index < max_likelihood_index:
                continue

            # found most likely ball so far
            max_likelihood_index = likelihood_index

            # meets minimum requirements
            if self.__meets_minimum_ball_requirements(ball, match_radius, match_value):
                # Scale to original frame size
                ball.center = tuple((int(pos * self._frame_scaler) for pos in (int(x), int(y))))
                ball.radius = int(match_radius * self._frame_scaler)

            # Get angle between ball center and approximate robot chassis center
            ball.angle_from_center = get_object_target_lock_control_angle(
                center_reposition(
                    ball.center,
                    frame
                ),
                frame
            )

        return None if ball.center is None else ball

    def __get_ball_likelihood_parameters(self, frame, contour, x, y, radius):
        area = self.cv2.contourArea(contour)
        match_contour = self.__get_circular_match_contour(frame, x, y, radius)
        match_value = self.cv2.matchShapes(contour, match_contour, 1, 0.0)  # closer to zero is a better match

        return area, match_value

    def __get_circular_match_contour(self, resized_frame, x, y, radius):
        mask_to_compare = np.zeros(resized_frame.shape[:2], dtype="uint8")
        self.cv2.circle(mask_to_compare, (int(x), int(y)), int(radius), 255, -1)
        contours_compare = self.cv2.findContours(mask_to_compare, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
        contours_compare = grab_contours(contours_compare)
        return max(contours_compare, key=self.cv2.contourArea)
