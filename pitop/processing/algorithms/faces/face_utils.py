from imutils import face_utils
import numpy as np
import math


def get_face_angle(face_features):
    """
    Returns angle in degrees of face from dlib face features
    :param face_features: dlib face features
    :return: angle of face in degrees
    """
    left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    jaw_start, jaw_end = face_utils.FACIAL_LANDMARKS_68_IDXS["jaw"]

    left_eye = face_features[left_eye_start:left_eye_end]
    right_eye = face_features[right_eye_start:right_eye_end]

    left_eye_position = np.average(left_eye, axis=0)
    right_eye_position = np.average(right_eye, axis=0)

    position_diff = left_eye_position - right_eye_position

    x_diff, y_diff = position_diff

    angle = math.degrees(math.atan(y_diff/x_diff))

    return angle


central_face_features = (27, 28, 29, 30, 33, 51, 62, 66, 57, 8)


def get_face_angle_2(face_features):
    """

    :param face_features:
    :return:
    """
    central_points = np.take(face_features, central_face_features, axis=0)
    x = central_points[:, 0]
    y = central_points[:, 1]

    A = np.vstack([x, np.ones(len(x))]).T

    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    angle = math.degrees(math.atan(-m))

    if angle > 0:
        angle = 90 - angle
    else:
        angle = -90 - angle

    return angle
