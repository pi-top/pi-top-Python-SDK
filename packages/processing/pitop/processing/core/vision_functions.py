from pitop.core.import_opencv import import_opencv


def import_imutils():
    try:
        import imutils

        return imutils
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "imutils Python library is not installed. You can install it by running 'sudo apt install python3-imutils'."
        ) from None


def import_face_utils():
    try:
        import imutils.face_utils

        return imutils.face_utils
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "imutils Python library is not installed. You can install it by running 'sudo apt install python3-imutils'."
        ) from None


def import_dlib():
    try:
        import dlib

        return dlib
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "dlib Python library is not installed. You can install it by running 'sudo apt install python3-dlib'."
        ) from None


def color_mask(frame, hsv_lower, hsv_upper):
    cv2 = import_opencv()
    # apply gaussian blur to smooth out the frame
    blur = cv2.blur(frame, (9, 9))

    # Convert BGR to HSV
    hsv_frame = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv_frame, hsv_lower, hsv_upper)

    return mask


def find_largest_contour(frame):
    cv2 = import_opencv()
    # Find the contours of the frame. RETR_EXTERNAL: retrieves only the extreme outer contours
    from imutils import grab_contours

    contours = grab_contours(
        cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    )

    # Find the biggest contour (if detected)
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
    else:
        # no contours found, set to None
        largest_contour = None

    return largest_contour


def find_centroid(contour):
    cv2 = import_opencv()

    if contour is not None:
        moments = cv2.moments(contour)
        # add 1e-5 to avoid division by zero (standard docs.opencv.org practice apparently)
        centroid_x = int(moments["m10"] / (moments["m00"] + 1e-5))
        centroid_y = int(moments["m01"] / (moments["m00"] + 1e-5))
    else:
        # no centroid found, set to none and deal with this case as necessary
        centroid_x = None
        centroid_y = None

    return centroid_x, centroid_y


def find_largest_rectangle(rectangles):
    area = 0
    current_index = 0
    largest_index = 0
    for x, y, w, h in rectangles:
        current_area = w * h
        if current_area > area:
            area = current_area
            largest_index = current_index
        current_index += 1

    return rectangles[largest_index]


def center_reposition(center, frame):
    """Reposition center so that (0, 0) is in the middle of the frame and y is
    pointing up instead of the OpenCV standard where (0, 0) is at the top left
    and y is pointing down.

    :param center: OpenCV center (x, y)
    :param frame: Frame to reposition center within
    :return:
    """
    if center is None:
        return None
    # convert so (0, 0) is at the middle bottom of the frame
    center_x = center[0] - int(round(frame.shape[1] / 2))
    center_y = int(round(frame.shape[0] / 2)) - center[1]

    return center_x, center_y


def get_object_target_lock_control_angle(center, frame):
    """Retrieves an angle between the center of an object in the camera's view
    and the (approximate) robot chassis center.

    This can be used as input to a PID loop so the object is "target locked" - the robot drives to align itself with
    the object, i.e. aim to minimize difference between chassis angle and object angle.
    :param tuple center:
            (x, y) coordinates of the object in the camera's view where the center of the frame is (0, 0). Please note,
            this is different from the OpenCV convention where the top left of the frame is (0, 0).

    :param frame:
            OpenCV frame that has the same scale used for center parameter - this function uses the dimensions of
            the frame.
    :return float angle: Angle in degrees to 1 decimal place
    """
    from math import degrees

    from numpy import arctan

    if center is None:
        return None
    # physically, this represents an approximation between chassis rotation center and camera
    # the PID loop will deal with basically anything > 1 here, but Kp, Ki and Kd would need to change
    # with (0, 0) in the middle of the frame, it is currently set to be half the frame height below the frame
    chassis_center_y = -int(frame.shape[1])

    # Clockwise is positive angle
    delta_y = abs(center[1] - chassis_center_y)

    return round(degrees(arctan(center[0] / delta_y)), 1)


def tuple_for_color_by_name(color_name, bgr=False):
    """Returns a tuple representing the provided `color_name`. The default
    color model used is RGB.

    :param color_name: string with the color name
    :param bgr: Boolean. If set to True, the color model of the returned
        tuple is set to BGR.
    :return: tuple
    """
    # Tested with red, green, blue
    if color_name == "green":
        # green: (0, 128, 0)
        # lime:  (0, 255, 0)
        color_name = "lime"

    from matplotlib import colors

    values = tuple(int(i * 255) for i in colors.to_rgb(color_name))
    if bgr:
        return values[::-1]
    return values
