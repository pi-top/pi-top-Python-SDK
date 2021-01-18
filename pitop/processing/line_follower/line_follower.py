import cv2
from numpy import arctan, pi, array

from .feedback_controller import FeedbackController
from .image_processor import ImageProcessor


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


class LineFollower:

    def __init__(self, image_resolution, drive_controller, linear_speed=0.8):
        self._frame_resolution = image_resolution
        self._image_processor = ImageProcessor(lower_blue, upper_blue, self._frame_resolution)
        self._chassis_controller = FeedbackController(linear_speed, drive_controller)
        self._chassis_controller.speed_linear_x = linear_speed
        self._centroid = (None, None)
        # physically, this represents an approximation between chassis rotation center and camera
        # the PID loop will deal with basically anything > 1 here, but Kp, Ki and Kd would need to change
        # with (0, 0) in the middle of the frame, it is currently set to be half the frame height below the frame
        self._chassis_center_y = -int(self._frame_resolution[1])
        self._camera_frame = None
        self._robot_view = None

    def find_line(self, frame):
        self._camera_frame = frame

        # get the centroid of the line
        self._centroid = self._image_processor.get_centroid(self._camera_frame)

        self._robot_view = self._image_processor.robot_view()

        if self._centroid[0] is None or self._centroid[1] is None:
            # line appears to be lost
            # TODO: on_line_lost event?
            return False, self._robot_view

        x, y = self.get_line_center()
        self.update_robot_controller(x, y)

        # TODO: on_line_found event?
        return True, self._robot_view

    def update_robot_controller(self, x, y):
        # calculate the control angle (state) to plug into the PID controller
        control_angle = self.__get_control_angle(x, y)

        # update PID controller
        self._chassis_controller.control_update(control_angle)

    def __get_control_angle(self, centroid_x, centroid_y):
        # we want a positive angle to indicate anticlockwise robot rotation per ChassisMoveController coordinate frame
        # therefore if the line is left of frame, vector angle will be positive and robot will rotate anticlockwise
        delta_y = abs(centroid_y - self._chassis_center_y)

        chassis_vector_angle = arctan(centroid_x / delta_y) * 180 / pi

        return chassis_vector_angle

    def get_line_center(self):
        return self._centroid[0], self._centroid[1]

    @property
    def linear_speed(self):
        return self._chassis_controller.speed_linear_x

    @linear_speed.setter
    def linear_speed(self, speed):
        self._chassis_controller.speed_linear_x = speed

    def get_contour_bound_parameters(self):
        x, y, w, h = self._image_processor.contour_bound_scale_up()
        return x, y, w, h

    def stop_robot(self):
        self._chassis_controller.stop_chassis()

    def exit(self):
        cv2.destroyAllWindows()
        self._chassis_controller.stop_chassis()
