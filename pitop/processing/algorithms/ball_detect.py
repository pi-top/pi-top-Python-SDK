from collections import deque
import numpy as np
import cv2
import imutils
from .line_detect import (
    get_control_angle,
    centroid_reposition
)
from pitop.core import ImageFunctions
from pitop.processing.utils.vision_functions import scale_frame


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


colour_ranges = {
    'red': {
        'lower': (150, 75, 75),
        'upper': (200, 255, 255)
    },
    'green': {
        'lower': (40, 100, 75),
        'upper': (90, 255, 255)
    },
    'blue': {
        'lower': (100, 100, 75),
        'upper': (140, 255, 255)
    }
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
detection_points = {
    "red": deque(maxlen=BUFFER_LENGTH),
    "green": deque(maxlen=BUFFER_LENGTH),
    "blue": deque(maxlen=BUFFER_LENGTH)
}


def colour_filter(frame, colour: str = "red", return_binary_mask=False, image_format: str = "PIL", image_return_format: str = "PIL"):
    if image_format.lower() == 'pil':
        frame = ImageFunctions.convert(frame, format="OpenCV")

    if colour.lower() not in ('red', 'green', 'blue'):
        raise ValueError('colour must be "red", "green" or "blue"')

    hsv_lower = colour_ranges[colour]['lower']
    hsv_upper = colour_ranges[colour]['upper']
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    mask = cv2.erode(mask, None, iterations=4)
    mask = cv2.dilate(mask, None, iterations=4)

    if not return_binary_mask:
        mask = cv2.bitwise_and(frame, frame, mask=mask)

    if image_return_format.lower() == 'pil':
        mask = ImageFunctions.convert(mask, format="PIL")

    return mask


def find_most_likely_ball(contours, colour, resized_frame):
    ball_center = None
    ball_radius = None
    if len(contours) > 0:

        max_likelihood_index = 0
        for contour in contours:
            # loop through all contours and store the most likely one's parameters
            (x, y), radius = cv2.minEnclosingCircle(contour)
            area = cv2.contourArea(contour)

            # compare found contour with a perfect circle contour to dismiss coloured objects that aren't round
            mask_to_compare = np.zeros(resized_frame.shape[:2], dtype="uint8")
            cv2.circle(mask_to_compare, (int(x), int(y)), int(radius), 255, -1)
            contours_compare = cv2.findContours(mask_to_compare, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_compare = imutils.grab_contours(contours_compare)
            c2 = max(contours_compare, key=cv2.contourArea)
            match_value = cv2.matchShapes(contour, c2, 1, 0.0)  # closer to zero is a better match

            # most likely ball is a mixture of largest area and one that is most "ball-shaped"
            likelihood_index = area / match_value

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


def process_frame_for_ball(frame, colours=("red",), image_return_format: str = "PIL", scale_factor=0.5):
    cv_frame = ImageFunctions.convert(frame, format="OpenCV")
    resized_frame = scale_frame(cv_frame, scale=scale_factor)

    if len(colours) > 3:
        raise ValueError('Cannot pass more than three colours.')

    ball_centers = {}
    ball_radii = {}
    ball_angles = {}
    ball_finds = {}
    for colour in colours:
        mask = colour_filter(resized_frame, colour=colour, return_binary_mask=True, image_format="OpenCV",
                             image_return_format="OpenCV")

        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)  # fixes problems with OpenCV changing their protocol

        ball_center, ball_radius = find_most_likely_ball(contours, colour, resized_frame)

        detection_points[colour].appendleft(ball_center)

        if ball_center is not None:
            # draw the circle and centroid on the frame, then update the list of tracked points
            cv2.circle(resized_frame, ball_center, ball_radius, (0, 255, 255), 2)
            cv2.circle(resized_frame, ball_center, 5, draw_colour[colour], -1)

            # Reposition centre so (0, 0) is in the middle for the user.
            # Keep scale as 1 as user sees scaled down 320x240 image in Further
            ball_center = centroid_reposition(ball_center, 1, resized_frame)
            ball_angle = get_control_angle(ball_center, resized_frame)

            ball_centers[colour] = ball_center
            ball_radii[colour] = ball_radius
            ball_angles[colour] = ball_angle
            ball_finds[colour] = True
        else:
            ball_centers[colour] = None
            ball_radii[colour] = None
            ball_angles[colour] = None
            ball_finds[colour] = False

        for i in range(1, len(detection_points[colour])):
            # if either of the tracked points are None, ignore them
            if detection_points[colour][i - 1] is None or detection_points[colour][i] is None:
                continue
            # otherwise, compute the thickness of the line and draw the connecting lines
            thickness = int(np.sqrt(BUFFER_LENGTH / float(i + 1)))

            cv2.line(resized_frame, detection_points[colour][i - 1], detection_points[colour][i],
                     draw_colour[colour], thickness)

    if image_return_format.lower() != 'opencv':
        robot_view = ImageFunctions.convert(resized_frame, format="PIL")
    else:
        robot_view = resized_frame

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
