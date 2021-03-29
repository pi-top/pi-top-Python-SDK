from imutils import face_utils
import numpy as np
import math


def get_face_angle(face_features):
    """
    Returns angle in degrees of face from dlib face features
    :param face_features: dlib face features
    :return: angle of face in degrees
    """
    left_start, left_end = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    right_start, right_end = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    left_eye = face_features[left_start:left_end]
    right_eye = face_features[right_start:right_end]

    left_eye_position = np.average(left_eye, axis=0)
    right_eye_position = np.average(right_eye, axis=0)

    position_diff = left_eye_position - right_eye_position

    x_diff, y_diff = position_diff

    angle = math.degrees(math.atan(y_diff/x_diff))

    return angle
