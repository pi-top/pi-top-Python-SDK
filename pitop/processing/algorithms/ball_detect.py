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
    'red': [
        {
            'lower': (150, 100, 100),
            'upper': (179, 255, 255)
        },
        {
            'lower': (0, 100, 100),
            'upper': (5, 255, 255)
        }
    ],
    'green': [{
        'lower': (60, 100, 100),
        'upper': (90, 255, 255)
    }],
    'blue': [{
        'lower': (100, 100, 100),
        'upper': (130, 255, 255)
    }]
}

ball_match_limits = {
    'red': 0.1,  # red needs to be a higher limit since some skin types are redish in color
    'green': 0.05,
    'blue': 0.05
}

MIN_BALL_RADIUS = 5
BALL_CLOSE_RADIUS = 50
DETECTION_POINTS_BUFFER_LENGTH = 64


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
        self._detection_points = {
            "red": deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH),
            "green": deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH),
            "blue": deque(maxlen=DETECTION_POINTS_BUFFER_LENGTH)
        }
        self._frame_scaler = None

        # Enable FPS if environment variable is set
        self._print_fps = getenv('PT_ENABLE_FPS', "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def detect(self, frame, color: Union[str, tuple] = "red"):
        colors = self.__grab_colors(color)
        cv_frame, resized_frame = self.__prepare_frames(frame)

        ball_centers = {}
        ball_radii = {}
        ball_angles = {}
        ball_finds = {}
        robot_view = cv_frame.copy()
        for color in colors:
            ball_center, ball_radius = self.__find_most_likely_ball(color, resized_frame)

            if ball_center is not None:
                ball_center, ball_radius = self.__reposition_to_original_frame_size(ball_center, ball_radius)

                self._detection_points[color].appendleft(ball_center)

                self.__draw_ball_position(robot_view, color, ball_center, ball_radius)

                ball_center = center_reposition(ball_center, robot_view)
                ball_angle = get_object_target_lock_control_angle(ball_center, robot_view)

                ball_centers[color] = ball_center
                ball_radii[color] = ball_radius
                ball_angles[color] = ball_angle
                ball_finds[color] = True
            else:
                self._detection_points[color].appendleft(None)
                ball_centers[color] = None
                ball_radii[color] = None
                ball_angles[color] = None
                ball_finds[color] = False

            self.__draw_ball_contrail(robot_view, color)

        if self.format.lower() != 'opencv':
            robot_view = ImageFunctions.convert(robot_view, format="PIL")

        ball_data = self.__prepare_return_data(robot_view, colors, ball_finds, ball_centers, ball_radii, ball_angles)

        if self._print_fps:
            self._fps.update()

        return ball_data

    @staticmethod
    def __prepare_return_data(robot_view, colors, ball_finds, ball_centers, ball_radii, ball_angles):
        ball_data = DotDict({})
        ball_data["robot_view"] = robot_view

        for color in colors:
            ball_data[color] = DotDict({
                "found": ball_finds[color],
                "center": ball_centers[color],
                "radius": ball_radii[color],
                "angle": ball_angles[color]
            })

        if len(colors) == 1:
            # if only searching one color, add convenience data so ball_data.data_type can be used directly
            color = colors[0]
            ball_data["found"] = ball_finds[color]
            ball_data["center"] = ball_centers[color]
            ball_data["radius"] = ball_radii[color]
            ball_data["angle"] = ball_angles[color]

        return ball_data

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")

    def __prepare_frames(self, frame):
        frame = ImageFunctions.convert(frame, format='OpenCV')

        if self._frame_scaler is None:
            height, width = frame.shape[0:2]
            self._frame_scaler = width / self._process_image_width

        resized_frame = resize(frame, width=self._process_image_width)

        return frame, resized_frame

    def __draw_ball_position(self, frame, color, ball_center, ball_radius):
        self.cv2.circle(frame, ball_center, ball_radius, (0, 255, 255), 2)
        self.cv2.circle(frame, ball_center, 5, tuple_for_color_by_name(color), -1)

    def __draw_ball_contrail(self, frame, color):
        for i in range(1, len(self._detection_points[color])):
            if self._detection_points[color][i - 1] is None or self._detection_points[color][i] is None:
                continue
            thickness = int(np.sqrt(DETECTION_POINTS_BUFFER_LENGTH / float(i + 1)))

            self.cv2.line(frame, self._detection_points[color][i - 1], self._detection_points[color][i],
                          tuple_for_color_by_name(color), thickness)

    def __reposition_to_original_frame_size(self, ball_center, ball_radius):
        ball_center = tuple((int(item * self._frame_scaler) for item in ball_center))
        ball_radius = int(ball_radius * self._frame_scaler)

        return ball_center, ball_radius

    @staticmethod
    def __grab_colors(color):
        colors = None
        if type(color) == str:
            colors = (color,)
        elif type(color) == tuple:
            colors = color
        if len(colors) > 3:
            raise ValueError('Cannot pass more than three colors.')

        return colors

    def color_filter(self,
                     frame,
                     color: str = "red",
                     return_binary_mask: bool = False,
                     format: str = "PIL"
                     ):

        frame = ImageFunctions.convert(frame, format="OpenCV")

        if color.lower() not in ('red', 'green', 'blue'):
            raise ValueError('Color must be "red", "green" or "blue"')

        blurred = self.cv2.blur(frame, (11, 11))
        hsv = self.cv2.cvtColor(blurred, self.cv2.COLOR_BGR2HSV)

        masks = []
        for color_range in color_ranges[color]:
            hsv_lower = color_range['lower']
            hsv_upper = color_range['upper']
            mask = self.cv2.inRange(hsv, hsv_lower, hsv_upper)
            masks.append(mask)
        mask = sum(masks)

        mask = self.cv2.erode(mask, None, iterations=1)
        mask = self.cv2.dilate(mask, None, iterations=1)

        if not return_binary_mask:
            mask = self.cv2.bitwise_and(frame, frame, mask=mask)

        if format.lower() == 'pil':
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

    def __find_most_likely_ball(self, color, resized_frame):
        ball_center = None
        ball_radius = None

        contours = self.__find_contours(resized_frame, color)
        if len(contours) > 0:
            max_likelihood_index = 0
            for contour in contours:
                (x, y), radius = self.cv2.minEnclosingCircle(contour)
                area, match_value = self.__get_ball_likelihood_parameters(resized_frame, contour, x, y, radius)

                # most likely ball is a mixture of largest area and one that is most "ball-shaped"
                likelihood_index = area / (match_value + 1e-5)
                if likelihood_index > max_likelihood_index:
                    max_likelihood_index = likelihood_index
                    if self.__meets_minimum_ball_requirements(color, match_value, radius):
                        ball_center = (int(x), int(y))
                        ball_radius = int(radius)

        return ball_center, ball_radius

    def __get_ball_likelihood_parameters(self, frame, contour, x, y, radius):
        area = self.cv2.contourArea(contour)
        match_contour = self.__get_circular_match_contour(frame, x, y, radius)
        match_value = self.cv2.matchShapes(contour, match_contour, 1, 0.0)  # closer to zero is a better match

        return area, match_value

    @staticmethod
    def __meets_minimum_ball_requirements(color, match_value, radius):
        if match_value < ball_match_limits[color] or radius > BALL_CLOSE_RADIUS:
            if radius > MIN_BALL_RADIUS:
                return True
        return False

    def __get_circular_match_contour(self, resized_frame, x, y, radius):
        mask_to_compare = np.zeros(resized_frame.shape[:2], dtype="uint8")
        self.cv2.circle(mask_to_compare, (int(x), int(y)), int(radius), 255, -1)
        contours_compare = self.cv2.findContours(mask_to_compare, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
        contours_compare = grab_contours(contours_compare)
        return max(contours_compare, key=self.cv2.contourArea)
