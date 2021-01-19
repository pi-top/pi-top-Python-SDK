import cv2
from numpy import array

from pitop.processing.utils.vision_functions import (
    colour_mask,
    find_centroid,
    find_largest_contour
)

# define range of blue color in HSV-> H: 0-179, S: 0-255, V: 0-255
# broken out like this for easy conversion into CV units (will move somewhere more logical in future)
__hue_lower = 160
__hue_upper = 280
__sat_lower = 0.3
__sat_upper = 1.0
__val_lower = 0.5
__val_upper = 1.0
__cv_hue_lower = int(__hue_lower / 2)
__cv_hue_upper = int(__hue_upper / 2)
__cv_sat_lower = int(__sat_lower * 255)
__cv_sat_upper = int(__sat_upper * 255)
__cv_val_lower = int(__val_lower * 255)
__cv_val_upper = int(__val_upper * 255)
__lower_blue = array([__cv_hue_lower, __cv_sat_lower, __cv_val_lower])
__upper_blue = array([__cv_hue_upper, __cv_sat_upper, __cv_val_upper])


class LineDetector:
    def __init__(self, camera_resolution, image_scale=0.5, hsv_lower=__lower_blue, hsv_upper=__upper_blue):
        self._hsv_lower = hsv_lower
        self._hsv_upper = hsv_upper
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

    def find_line(self, frame):
        centroid = self.__get_centroid(frame)
        found_line = centroid[0] is not None and centroid[1] is not None
        return (found_line, self.__robot_view())

    def __get_centroid(self, frame):
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

    def __robot_view(self):
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
