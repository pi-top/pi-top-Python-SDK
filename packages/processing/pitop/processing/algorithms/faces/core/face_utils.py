import math
from collections import OrderedDict

import numpy as np

FACIAL_LANDMARKS_68_IDXS = OrderedDict(
    [
        ("mouth", (48, 68)),
        ("inner_mouth", (60, 68)),
        ("right_eyebrow", (17, 22)),
        ("left_eyebrow", (22, 27)),
        ("right_eye", (36, 42)),
        ("left_eye", (42, 48)),
        ("nose", (27, 36)),
        ("jaw", (0, 17)),
    ]
)


FACIAL_LANDMARKS_5_IDXS = OrderedDict(
    [("right_eye", (2, 4)), ("left_eye", (0, 2)), ("nose", 4)]
)


def get_face_angle(face_features):
    """Returns angle in degrees of face from dlib face features.

    :param face_features: dlib face features (either 5 landmark or 68
        landmark version)
    :return: angle of face in degrees
    """
    if len(face_features) == 68:
        # https://pyimagesearch.com/wp-content/uploads/2017/04/facial_landmarks_68markup.jpg
        # note: array is 0-indexed, image annotations are 1-indexed

        left_eye_start, left_eye_end = FACIAL_LANDMARKS_68_IDXS["left_eye"]
        right_eye_start, right_eye_end = FACIAL_LANDMARKS_68_IDXS["right_eye"]
        left_eyebrow_start, left_eyebrow_end = FACIAL_LANDMARKS_68_IDXS["left_eyebrow"]
        right_eyebrow_start, right_eyebrow_end = FACIAL_LANDMARKS_68_IDXS[
            "right_eyebrow"
        ]
        jaw_start, jaw_end = FACIAL_LANDMARKS_68_IDXS["jaw"]

        left_eye = face_features[left_eye_start:left_eye_end]
        right_eye = face_features[right_eye_start:right_eye_end]

        left_eyebrow = face_features[left_eyebrow_start:left_eyebrow_end]
        right_eyebrow = face_features[right_eyebrow_start:right_eyebrow_end]

        left_jaw = face_features[(jaw_end + 1) // 2 : jaw_end]
        right_jaw = face_features[jaw_start : (jaw_end - 1) // 2]

        left_mouth = np.take(face_features, (52, 53, 54, 55, 56, 63, 64, 65), axis=0)
        right_mouth = np.take(face_features, (48, 49, 50, 58, 59, 60, 61, 67), axis=0)

        all_left_points = np.vstack((left_eye, left_eyebrow, left_jaw, left_mouth))
        all_right_points = np.vstack((right_eye, right_eyebrow, right_jaw, right_mouth))

    elif len(face_features) == 5:
        left_eye_start, left_eye_end = FACIAL_LANDMARKS_5_IDXS["left_eye"]
        right_eye_start, right_eye_end = FACIAL_LANDMARKS_5_IDXS["right_eye"]
        all_left_points = face_features[left_eye_start:left_eye_end]
        all_right_points = face_features[right_eye_start:right_eye_end]

    else:
        raise ValueError("dlib face features not recognised, please try again")

    left_centroid = np.average(all_left_points, axis=0)
    right_centroid = np.average(all_right_points, axis=0)

    position_diff = left_centroid - right_centroid

    x_diff, y_diff = position_diff

    angle = -math.degrees(math.atan(y_diff / x_diff))

    return round(angle, 1)


def pupil_distance(face_features):
    """
    :param face_features: dlib face features (either 5 landmark or 68 landmark version)
    :return: Scalar distance between left eye center and right eye center
    :rtype: float
    """
    return round(
        np.linalg.norm(
            np.asarray(left_eye_center(face_features))
            - np.asarray(right_eye_center(face_features))
        ),
        1,
    )


def left_eye_center(face_features):
    """Left eye is assumed to be on the right of the face in the image frame
    (i.e. from camera's point of view).

    :param face_features: dlib face features (either 5 landmark or 68
        landmark version)
    :return: (x, y) position of left eye
    :rtype: tuple
    """
    return feature_center(eye_landmarks(face_features, "left_eye"))


def right_eye_center(face_features):
    """Right eye is assumed to be on the left of the face in the image frame
    (i.e. from camera's point of view).

    :param face_features: dlib face features (either 5 landmark or 68
        landmark version)
    :return: (x, y) position of right eye
    :rtype: tuple
    """
    return feature_center(eye_landmarks(face_features, "right_eye"))


def left_eye_dimensions(face_features):
    """Left eye is assumed to be on the right of the face in the image frame
    (i.e. from camera's point of view).

    :param face_features: dlib face features (either 5 landmark or 68
        landmark version)
    :return: (width, height) for 68-landmark version and (width, None)
        for 5-landmark version
    :rtype: tuple
    """
    return eye_dimensions(face_features, "left_eye")


def right_eye_dimensions(face_features):
    """Right eye is assumed to be on the left of the face in the image frame
    (i.e. from camera's point of view).

    :param face_features: dlib face features (either 5 landmark or 68
        landmark version)
    :return: (width, height) for 68-landmark version and (width, None)
        for 5-landmark version
    :rtype: tuple
    """
    return eye_dimensions(face_features, "right_eye")


def eye_dimensions(face_features, position: str):
    landmarks = eye_landmarks(face_features, position)
    if len(face_features) == 68:
        width = round(np.linalg.norm(landmarks[0] - landmarks[3]), 1)
        height = round(
            (
                np.linalg.norm(landmarks[1] - landmarks[5])
                + np.linalg.norm(landmarks[2] - landmarks[4])
            )
            / 2,
            1,
        )
        return width, height
    elif len(face_features) == 5:
        width = np.linalg.norm(landmarks[0] - landmarks[1])
        return width, None


def eye_landmarks(face_features, position: str):
    eye_start, eye_end = get_landmarks_dict(face_features)[position]
    return face_features[eye_start:eye_end]


def mouth_center(face_features):
    return feature_center(mouth_landmarks(face_features))


def mouth_landmarks(face_features):
    if len(face_features) == 5:
        raise ValueError(
            "Not compatible with 5-landmark version, use 68-landmark version instead."
        )
    mouth_start, mouth_end = FACIAL_LANDMARKS_68_IDXS["mouth"]
    return face_features[mouth_start:mouth_end]


def mouth_dimensions(face_features):
    landmarks = mouth_landmarks(face_features)
    width = round(np.linalg.norm(landmarks[0] - landmarks[6]), 1)
    height = round(np.linalg.norm(landmarks[3] - landmarks[9]), 1)
    return width, height


def nose_bottom(face_features):
    """
    :param face_features: dlib face features (either 5 landmark or 68 landmark version)
    :return: (x, y) position of the bottom of the nose
    :rtype: tuple
    """
    if len(face_features) == 68:
        return tuple(np.take(face_features, 33, axis=0).astype(int))
    elif len(face_features) == 5:
        return tuple(np.take(face_features, 4, axis=0).astype(int))
    else:
        raise ValueError("dlib face features not recognised, please try again")


def feature_center(feature_landmarks):
    return tuple(np.mean(feature_landmarks, axis=0).astype(int))


def get_landmarks_dict(face_features):
    if len(face_features) == 68:
        landmarks_dict = FACIAL_LANDMARKS_68_IDXS
    elif len(face_features) == 5:
        landmarks_dict = FACIAL_LANDMARKS_5_IDXS
    else:
        raise ValueError("dlib face features not recognised, please try again")

    return landmarks_dict
