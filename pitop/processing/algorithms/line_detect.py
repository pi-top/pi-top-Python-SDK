from numpy import arctan, array, pi

from pitop.processing.utils.vision_functions import (
    colour_mask,
    find_centroid,
    find_largest_contour,
    scale_frame,
)
from pitop.core import ImageFunctions


def import_opencv():
    try:
        import cv2
        return cv2
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "OpenCV Python library is not installed. You can install it by running 'sudo apt install python3-opencv'.") from None


def calculate_blue_limits():
    # define range of blue color in HSV-> H: 0-179, S: 0-255, V: 0-255
    # broken out like this for easy conversion into CV units (will move somewhere more logical in future)
    hue_lower = 160
    hue_upper = 280
    sat_lower = 0.3
    sat_upper = 1.0
    val_lower = 0.5
    val_upper = 1.0
    cv_hue_lower = int(hue_lower / 2)
    cv_hue_upper = int(hue_upper / 2)
    cv_sat_lower = int(sat_lower * 255)
    cv_sat_upper = int(sat_upper * 255)
    cv_val_lower = int(val_lower * 255)
    cv_val_upper = int(val_upper * 255)
    lower_blue = array([cv_hue_lower, cv_sat_lower, cv_val_lower])
    upper_blue = array([cv_hue_upper, cv_sat_upper, cv_val_upper])
    return lower_blue, upper_blue


def process_frame_for_line(frame, image_format="PIL", scale_factor=0.5):
    cv2 = import_opencv()
    cv_frame = ImageFunctions.pil_to_opencv(frame)

    resized_frame = scale_frame(cv_frame, scale=scale_factor)
    hsv_lower, hsv_upper = calculate_blue_limits()
    image_mask = colour_mask(resized_frame, hsv_lower, hsv_upper)
    line_contour = find_largest_contour(image_mask)

    centroid = None
    scaled_image_centroid = None
    rectangle_dimensions = None
    if line_contour is not None:
        # find centroid of contour
        scaled_image_centroid = find_centroid(line_contour)
        centroid = centroid_reposition(scaled_image_centroid, 1, resized_frame)
        bounding_rectangle = cv2.boundingRect(line_contour)
        rectangle_dimensions = bounding_rectangle[2:5]

    robot_view_img = robot_view(resized_frame, image_mask, line_contour, scaled_image_centroid)

    if image_format.lower() != 'opencv':
        robot_view_img = ImageFunctions.opencv_to_pil(robot_view_img)

    class dotdict(dict):
        """dot.notation access to dictionary attributes"""
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    return dotdict({
        "line_center": centroid,
        "robot_view": robot_view_img,
        "rectangle_dimensions": rectangle_dimensions,
        "angle": get_control_angle(centroid, robot_view_img),
    })


def get_control_angle(centroid, frame):
    if centroid is None:
        return 0
    # physically, this represents an approximation between chassis rotation center and camera
    # the PID loop will deal with basically anything > 1 here, but Kp, Ki and Kd would need to change
    # with (0, 0) in the middle of the frame, it is currently set to be half the frame height below the frame
    chassis_center_y = -int(frame.size[1])

    # we want a positive angle to indicate anticlockwise robot rotation per ChassisMoveController coordinate frame
    # therefore if the line is left of frame, vector angle will be positive and robot will rotate anticlockwise
    delta_y = abs(centroid[1] - chassis_center_y)

    return arctan(centroid[0] / delta_y) * 180.0 / pi


def centroid_reposition(centroid, scale, frame):
    if centroid is None:
        return None
    # scale centroid so it matches original camera frame resolution
    centroid_x = int(centroid[0]/scale)
    centroid_y = int(centroid[1]/scale)
    # convert so (0, 0) is at the middle bottom of the frame
    centroid_x = centroid_x - int(frame.shape[1] / 2)
    centroid_y = int(frame.shape[0] / 2) - centroid_y

    return centroid_x, centroid_y


def robot_view(frame, image_mask, line_contour, centroid):
    cv2 = import_opencv()
    masked_image = cv2.bitwise_and(frame, frame, mask=image_mask)

    # draw contour lines on robot view
    if line_contour is not None:
        cv2.drawContours(masked_image, [line_contour], 0, (100, 60, 240), 2)
        draw_contour_bound(masked_image, line_contour)

    if centroid:
        cv2.drawMarker(masked_image,
                       (centroid[0], centroid[1]),
                       (100, 60, 240),
                       markerType=cv2.MARKER_CROSS,
                       markerSize=20,
                       thickness=4,
                       line_type=cv2.FILLED)
    return masked_image


def draw_contour_bound(image, contour):
    cv2 = import_opencv()
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
