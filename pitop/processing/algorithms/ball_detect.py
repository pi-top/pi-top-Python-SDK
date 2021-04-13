from collections import deque
import numpy as np
from pitop.core import ImageFunctions
from pitop.processing.utils.vision_functions import (
    center_reposition,
    get_control_angle,
)
from typing import Union
from imutils import resize, grab_contours
from imutils.video import FPS
from pitop.core.data_stuctures import DotDict
import atexit
from pitop.processing.utils.vision_functions import import_opencv

colour_ranges = {
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

draw_colour = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0)
}

ball_match_limits = {
    'red': 0.1,  # red needs to be a higher limit since some skin types are redish in colour
    'green': 0.05,
    'blue': 0.05
}

MIN_BALL_RADIUS = 5
BALL_CLOSE_RADIUS = 50
BUFFER_LENGTH = 64


class BallDetector:
    def __init__(self,
                 process_image_width: int = 320,
                 input_format: str = "PIL",
                 output_format: str = "PIL",
                 print_fps: bool = False):
        """
        :param int process_image_width: image width to scale to for image processing
        :param str input_format: input image format
        :param str output_format: output image format
        :param bool print_fps: Boolean that controls whether the algorithm's FPS is printed upon program exit
        """
        self.cv2 = import_opencv()
        self._process_image_width = process_image_width
        self._input_format = input_format
        self._output_format = output_format
        self._detection_points = {
            "red": deque(maxlen=BUFFER_LENGTH),
            "green": deque(maxlen=BUFFER_LENGTH),
            "blue": deque(maxlen=BUFFER_LENGTH)
        }
        self._frame_scaler = None
        self._print_fps = print_fps
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def detect(self, frame, colour: Union[str, tuple] = "red"):
        colours = self.__grab_colours(colour)
        resized_frame = self.__prepare_frame(frame)

        ball_centers = {}
        ball_radii = {}
        ball_angles = {}
        ball_finds = {}
        robot_view = frame.copy()
        for colour in colours:
            contours = self.__find_contours(resized_frame, colour)
            ball_center, ball_radius = self.__find_most_likely_ball(contours, colour, resized_frame)

            if ball_center is not None:
                ball_center, ball_radius = self.__reposition_to_original_frame_size(ball_center, ball_radius)

                self._detection_points[colour].appendleft(ball_center)

                self.__draw_ball_position(robot_view, colour, ball_center, ball_radius)

                ball_center = center_reposition(ball_center, robot_view)
                ball_angle = get_control_angle(ball_center, robot_view)

                ball_centers[colour] = ball_center
                ball_radii[colour] = ball_radius
                ball_angles[colour] = ball_angle
                ball_finds[colour] = True
            else:
                self._detection_points[colour].appendleft(None)
                ball_centers[colour] = None
                ball_radii[colour] = None
                ball_angles[colour] = None
                ball_finds[colour] = False

            self.__draw_ball_contrail(robot_view, colour)

        if self._output_format.lower() != 'opencv':
            robot_view = ImageFunctions.convert(robot_view, format="PIL")

        ball_data = self.__prepare_return_data(robot_view, colours, ball_finds, ball_centers, ball_radii, ball_angles)

        if self._print_fps:
            self._fps.update()

        return ball_data

    @staticmethod
    def __prepare_return_data(robot_view, colours, ball_finds, ball_centers, ball_radii, ball_angles):
        ball_data = DotDict({})
        ball_data["robot_view"] = robot_view

        for colour in colours:
            ball_data[colour] = DotDict({
                "found": ball_finds[colour],
                "center": ball_centers[colour],
                "radius": ball_radii[colour],
                "angle": ball_angles[colour]
            })

        if len(colours) == 1:
            # if only searching one colour, add convenience data so ball_data.data_type can be used directly
            colour = colours[0]
            ball_data["found"] = ball_finds[colour]
            ball_data["center"] = ball_centers[colour]
            ball_data["radius"] = ball_radii[colour]
            ball_data["angle"] = ball_angles[colour]

        return ball_data

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")

    def __prepare_frame(self, frame):
        if self._input_format.lower() == "pil":
            frame = ImageFunctions.convert(frame, format='OpenCV')

        if self._frame_scaler is None:
            height, width = frame.shape[0:2]
            self._frame_scaler = width / self._process_image_width

        resized_frame = resize(frame, width=self._process_image_width)

        return resized_frame

    def __draw_ball_position(self, frame, colour, ball_center, ball_radius):
        self.cv2.circle(frame, ball_center, ball_radius, (0, 255, 255), 2)
        self.cv2.circle(frame, ball_center, 5, draw_colour[colour], -1)

    def __draw_ball_contrail(self, frame, colour):
        for i in range(1, len(self._detection_points[colour])):
            if self._detection_points[colour][i - 1] is None or self._detection_points[colour][i] is None:
                continue
            thickness = int(np.sqrt(BUFFER_LENGTH / float(i + 1)))

            self.cv2.line(frame, self._detection_points[colour][i - 1], self._detection_points[colour][i],
                          draw_colour[colour], thickness)

    def __reposition_to_original_frame_size(self, ball_center, ball_radius):
        ball_center = tuple((int(item * self._frame_scaler) for item in ball_center))
        ball_radius = int(ball_radius * self._frame_scaler)

        return ball_center, ball_radius

    @staticmethod
    def __grab_colours(colour):
        colours = None
        if type(colour) == str:
            colours = (colour,)
        elif type(colour) == tuple:
            colours = colour
        if len(colours) > 3:
            raise ValueError('Cannot pass more than three colours.')

        return colours

    def colour_filter(self,
                      frame,
                      colour: str = "red",
                      return_binary_mask: bool = False,
                      input_format: str = "PIL",
                      output_format: str = "PIL"
                      ):

        if input_format.lower() == 'pil':
            frame = ImageFunctions.convert(frame, format="OpenCV")

        if colour.lower() not in ('red', 'green', 'blue'):
            raise ValueError('Colour must be "red", "green" or "blue"')

        blurred = self.cv2.blur(frame, (11, 11))
        hsv = self.cv2.cvtColor(blurred, self.cv2.COLOR_BGR2HSV)

        masks = []
        for colour_range in colour_ranges[colour]:
            hsv_lower = colour_range['lower']
            hsv_upper = colour_range['upper']
            mask = self.cv2.inRange(hsv, hsv_lower, hsv_upper)
            masks.append(mask)
        mask = sum(masks)

        mask = self.cv2.erode(mask, None, iterations=1)
        mask = self.cv2.dilate(mask, None, iterations=1)

        if not return_binary_mask:
            mask = self.cv2.bitwise_and(frame, frame, mask=mask)

        if output_format.lower() == 'pil':
            mask = ImageFunctions.convert(mask, format="PIL")

        return mask

    def __find_contours(self, frame, colour):
        mask = self.colour_filter(frame, colour=colour, return_binary_mask=True, input_format="OpenCV",
                                  output_format="OpenCV")

        contours = self.cv2.findContours(mask.copy(), self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
        contours = grab_contours(contours)  # fixes problems with OpenCV changing their protocol
        return contours

    def __find_most_likely_ball(self, contours, colour, resized_frame):
        ball_center = None
        ball_radius = None
        if len(contours) > 0:

            max_likelihood_index = 0
            for contour in contours:
                # loop through all contours and store the most likely one's parameters
                (x, y), radius = self.cv2.minEnclosingCircle(contour)
                area = self.cv2.contourArea(contour)

                # compare found contour with a perfect circle contour to dismiss coloured objects that aren't round
                match_contour = self.__get_circular_match_contour(resized_frame, x, y, radius)
                match_value = self.cv2.matchShapes(contour, match_contour, 1, 0.0)  # closer to zero is a better match

                # most likely ball is a mixture of largest area and one that is most "ball-shaped"
                likelihood_index = area / (match_value + 1e-5)

                # check if this contour is more likely than the last
                if likelihood_index > max_likelihood_index:
                    # save to new max
                    max_likelihood_index = likelihood_index
                    # check if the ball is circular. Or if it's so big it's just close to the camera and occluded
                    if match_value < ball_match_limits[colour] or radius > BALL_CLOSE_RADIUS:
                        # check if it meets the minimum ball radius
                        if radius > MIN_BALL_RADIUS:
                            # ok, we're finally happy that this is an actual ball
                            # store the values to be used as the most likely ball in frame
                            ball_center = (int(x), int(y))
                            ball_radius = int(radius)

        return ball_center, ball_radius

    def __get_circular_match_contour(self, resized_frame, x, y, radius):
        mask_to_compare = np.zeros(resized_frame.shape[:2], dtype="uint8")
        self.cv2.circle(mask_to_compare, (int(x), int(y)), int(radius), 255, -1)
        contours_compare = self.cv2.findContours(mask_to_compare, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
        contours_compare = grab_contours(contours_compare)
        return max(contours_compare, key=self.cv2.contourArea)
