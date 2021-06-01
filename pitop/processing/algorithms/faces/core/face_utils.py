def get_face_angle(face_features):
    """Returns angle in degrees of face from dlib face features.

    :param face_features: dlib face features (either 5 landmark or 68 landmark version)
    :return: angle of face in degrees
    """
    from imutils import face_utils
    import numpy as np
    import math

    if len(face_features) == 68:
        # https://pyimagesearch.com/wp-content/uploads/2017/04/facial_landmarks_68markup.jpg
        # note: array is 0-indexed, image annotations are 1-indexed

        left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
        right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
        left_eyebrow_start, left_eyebrow_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eyebrow"]
        right_eyebrow_start, right_eyebrow_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eyebrow"]
        jaw_start, jaw_end = face_utils.FACIAL_LANDMARKS_68_IDXS["jaw"]

        left_eye = face_features[left_eye_start:left_eye_end]
        right_eye = face_features[right_eye_start:right_eye_end]

        left_eyebrow = face_features[left_eyebrow_start: left_eyebrow_end]
        right_eyebrow = face_features[right_eyebrow_start: right_eyebrow_end]

        left_jaw = face_features[(jaw_end + 1) // 2:jaw_end]
        right_jaw = face_features[jaw_start:(jaw_end - 1) // 2]

        left_mouth = np.take(face_features, (52, 53, 54, 55, 56, 63, 64, 65), axis=0)
        right_mouth = np.take(face_features, (48, 49, 50, 58, 59, 60, 61, 67), axis=0)

        all_left_points = np.vstack((left_eye, left_eyebrow, left_jaw, left_mouth))
        all_right_points = np.vstack((right_eye, right_eyebrow, right_jaw, right_mouth))

    elif len(face_features) == 5:
        left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_5_IDXS["left_eye"]
        right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_5_IDXS["right_eye"]
        all_left_points = face_features[left_eye_start:left_eye_end]
        all_right_points = face_features[right_eye_start:right_eye_end]

    else:
        raise ValueError("dlib face features not recognised, please try again")

    left_centroid = np.average(all_left_points, axis=0)
    right_centroid = np.average(all_right_points, axis=0)

    position_diff = left_centroid - right_centroid

    x_diff, y_diff = position_diff

    angle = -math.degrees(math.atan(y_diff/x_diff))

    return round(angle, 1)
