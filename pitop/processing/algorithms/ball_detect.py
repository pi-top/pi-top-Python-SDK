from collections import deque
import numpy as np
import cv2
import imutils
from .line_detect import get_control_angle, centroid_reposition
from pitop.core import ImageFunctions
from pitop.processing.utils.vision_functions import (
    find_centroid,
    scale_frame
)


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


colours = {
    'red': {
        'lower': (150, 100, 50),
        'upper': (200, 255, 255)
    },
    'green': {
        'lower': (40, 100, 50),
        'upper': (80, 255, 255)
    },
    'blue': {
        'lower': (100, 100, 50),
        'upper': (140, 255, 255)
    }
}

BUFFER_LENGTH = 64
detection_points = deque(maxlen=BUFFER_LENGTH)


def ball_detect(frame, colour: str = "red", image_format="PIL", scale_factor=0.5):
    cv_frame = ImageFunctions.convert(frame, format="OpenCV")
    resized_frame = scale_frame(cv_frame, scale=scale_factor)
    if colour not in ('red', 'green', 'blue'):
        raise ValueError('colour must be "red", "green" or "blue"')

    hsv_lower = colours[colour]['lower']
    hsv_upper = colours[colour]['upper']
    blurred = cv2.GaussianBlur(resized_frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    center = None
    radius = None
    if len(contours) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)
        moment_matrix = cv2.moments(c)
        center = (int(moment_matrix["m10"] / moment_matrix["m00"]), int(moment_matrix["m01"] / moment_matrix["m00"]))
        # only proceed if the radius meets a minimum size
        if radius / resized_frame.size[0] > 5:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(resized_frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(resized_frame, center, 5, (0, 0, 255), -1)
            detection_points.appendleft(center)
        # reposition centre to (0, 0) is in the middle. Keep scale as 1 as user sees scaled down 320x240 image
        center = centroid_reposition(center, 1, resized_frame)

    for i in range(1, len(detection_points)):
        # if either of the tracked points are None, ignore
        # them
        if detection_points[i - 1] is None or detection_points[i] is None:
            continue
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(BUFFER_LENGTH / float(i + 1)) * 2.5)
        cv2.line(resized_frame, detection_points[i - 1], detection_points[i], (0, 0, 255), thickness)

    if image_format.lower() != 'opencv':
        robot_view = ImageFunctions.convert(cv_frame, format="PIL")
    else:
        robot_view = resized_frame

    angle = get_control_angle(center, frame)
    return DotDict({
        "center": center,
        "robot_view": robot_view,
        "radius": radius,
        "angle": angle
    })
