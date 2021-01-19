import cv2
from numpy import arctan, array, pi

from pitop.processing.utils.vision_functions import (
    colour_mask,
    find_centroid,
    find_largest_contour
)
from pitop.camera.pil_opencv_conversion import (
    pil_to_opencv,
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
    return (lower_blue, upper_blue)


def find_line(frame):
    line_detector = LineDetector(frame.size)
    centroid = line_detector._get_centroid(pil_to_opencv(frame))
    found_line = centroid[0] is not None and centroid[1] is not None

    control_angle = line_detector.get_control_angle(centroid)

    return (found_line, control_angle, line_detector._robot_view())


class LineDetector:
    def __init__(self, camera_resolution, image_scale=0.5, hsv_lower=None, hsv_upper=None):
        if hsv_lower is None or hsv_upper is None:
            _lower_blue, _upper_blue = calculate_blue_limits()

            if hsv_lower is None:
                self._hsv_lower = _lower_blue
            if hsv_upper is None:
                self._hsv_upper = _upper_blue

        self._image_scale = image_scale

        self._cam_image_width = camera_resolution[0]
        self._cam_image_height = camera_resolution[1]

        self._line_follower_image_width = 0
        self._line_follower_image_height = 0

        self._image_mask = None
        self._line_contour = None
        self._centroid = None
        self._image_processor_centroid = None
        self._scaled_frame = None

    def _get_centroid(self, frame):
        self._scaled_frame = self.__frame_scale_down(frame)
        self._image_mask = colour_mask(self._scaled_frame, self._hsv_lower, self._hsv_upper)
        self._line_contour = find_largest_contour(self._image_mask)
        if self._line_contour is not None:
            # find centroid of contour
            self._image_processor_centroid = find_centroid(self._line_contour)
            self._centroid = self.__centroid_reposition(self._image_processor_centroid)
        else:
            self._centroid = (None, None)
        return self._centroid

    def _robot_view(self):
        masked_image = cv2.bitwise_and(self._scaled_frame, self._scaled_frame, mask=self._image_mask)
        # draw contour lines on robot view
        if self._line_contour is not None:
            cv2.drawContours(masked_image, [self._line_contour], 0, (100, 60, 240), 2)
            self.__draw_contour_bound(masked_image)

        if self._centroid[0] is not None and self._centroid[1] is not None:
            cv2.drawMarker(masked_image, (self._image_processor_centroid[0], self._image_processor_centroid)[1], (100, 60, 240),
                           markerType=cv2.MARKER_CROSS, markerSize=20, thickness=4, line_type=cv2.FILLED)

        # draw centroid on robot view
        masked_image_scaled_up = self.__frame_scale_up(masked_image)
        return masked_image_scaled_up

    def __draw_contour_bound(self, image):
        x, y, w, h = cv2.boundingRect(self._line_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # def contour_bound_scale_up(self):
    #     x, y, w, h = [int(element / self._image_scale) for element in cv2.boundingRect(self._line_contour)]
    #     return x, y, w, h

    def __frame_scale_down(self, frame):
        self._line_follower_image_width = int(self._cam_image_width * self._image_scale)
        self._line_follower_image_height = int(self._cam_image_height * self._image_scale)
        dim = (self._line_follower_image_width, self._line_follower_image_height)

        scaled_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        return scaled_frame

    def __frame_scale_up(self, frame):
        return cv2.resize(frame, (self._cam_image_width, self._cam_image_height), interpolation=cv2.INTER_AREA)

    def __centroid_reposition(self, centroid):
        # scale centroid so it matches original camera frame resolution
        centroid_x = int(centroid[0]/self._image_scale)
        centroid_y = int(centroid[1]/self._image_scale)
        # convert so (0, 0) is at the middle bottom of the frame
        centroid_x = centroid_x - int(self._cam_image_width / 2)
        centroid_y = int(self._cam_image_height / 2) - centroid_y

        return centroid_x, centroid_y

    def get_control_angle(self, centroid):
        # physically, this represents an approximation between chassis rotation center and camera
        # the PID loop will deal with basically anything > 1 here, but Kp, Ki and Kd would need to change
        # with (0, 0) in the middle of the frame, it is currently set to be half the frame height below the frame
        chassis_center_y = -int(self._cam_image_width)

        # we want a positive angle to indicate anticlockwise robot rotation per ChassisMoveController coordinate frame
        # therefore if the line is left of frame, vector angle will be positive and robot will rotate anticlockwise
        delta_y = abs(centroid[1] - chassis_center_y)

        return arctan(centroid[0] / delta_y) * 180 / pi
