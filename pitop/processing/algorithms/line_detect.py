from numpy import array

from pitop.core import ImageFunctions
from pitop.core.data_structures import DotDict
from pitop.processing.core.vision_functions import (
    center_reposition,
    color_mask,
    find_centroid,
    find_largest_contour,
    get_object_target_lock_control_angle,
    import_opencv,
)


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


def process_frame_for_line(frame, image_format="PIL", process_image_width=320):
    cv2 = import_opencv()
    cv_frame = ImageFunctions.convert(frame, format="OpenCV")

    from imutils import resize

    resized_frame = resize(cv_frame, width=process_image_width)
    hsv_lower, hsv_upper = calculate_blue_limits()
    image_mask = color_mask(resized_frame, hsv_lower, hsv_upper)
    line_contour = find_largest_contour(image_mask)

    centroid = None
    scaled_image_centroid = None
    rectangle_dimensions = None
    angle = None
    if line_contour is not None:
        # find centroid of contour
        scaled_image_centroid = find_centroid(line_contour)
        centroid = center_reposition(scaled_image_centroid, resized_frame)
        bounding_rectangle = cv2.boundingRect(line_contour)
        rectangle_dimensions = bounding_rectangle[2:5]
        angle = get_object_target_lock_control_angle(centroid, resized_frame)

    robot_view_img = robot_view(
        resized_frame, image_mask, line_contour, scaled_image_centroid
    )

    if image_format.lower() != "opencv":
        robot_view_img = ImageFunctions.convert(robot_view_img, format="PIL")

    return DotDict(
        {
            "line_center": centroid,
            "robot_view": robot_view_img,
            "rectangle_dimensions": rectangle_dimensions,
            "angle": angle,
        }
    )


def robot_view(frame, image_mask, line_contour, centroid):
    cv2 = import_opencv()
    masked_image = cv2.bitwise_and(frame, frame, mask=image_mask)

    # draw contour lines on robot view
    if line_contour is not None:
        cv2.drawContours(masked_image, [line_contour], 0, (100, 60, 240), 2)
        draw_contour_bound(masked_image, line_contour)

    if centroid:
        cv2.drawMarker(
            masked_image,
            (centroid[0], centroid[1]),
            (100, 60, 240),
            markerType=cv2.MARKER_CROSS,
            markerSize=20,
            thickness=4,
            line_type=cv2.FILLED,
        )
    return masked_image


def draw_contour_bound(image, contour):
    cv2 = import_opencv()
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
