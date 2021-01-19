import cv2
from numpy import arctan, pi

from .feedback_controller import FeedbackController
from .line_detector import LineDetector


class LineFollower:
    def __init__(self, image_resolution, drive_controller, linear_speed=0.8):
        self._line_detector = LineDetector(image_resolution)

        self._chassis_controller = FeedbackController(linear_speed, drive_controller)
        self._chassis_controller.speed_linear_x = linear_speed
        self._centroid = (None, None)

        # physically, this represents an approximation between chassis rotation center and camera
        # the PID loop will deal with basically anything > 1 here, but Kp, Ki and Kd would need to change
        # with (0, 0) in the middle of the frame, it is currently set to be half the frame height below the frame
        self._chassis_center_y = -int(image_resolution[1])

    def find_line(self, frame):
        # get the centroid of the line
        self._centroid = self._line_detector.get_centroid(frame)

        robot_view = self._line_detector.robot_view()

        if self._centroid[0] is None or self._centroid[1] is None:
            # line appears to be lost
            # TODO: on_line_lost event?
            return False, robot_view

        # TODO: on_line_found event?
        return True, robot_view

    def update_robot_controller(self):
        # calculate the control angle (state) to plug into the PID controller
        control_angle = self.__get_control_angle(self._centroid)

        # update PID controller
        self._chassis_controller.control_update(control_angle)

    def __get_control_angle(self, centroid):
        # we want a positive angle to indicate anticlockwise robot rotation per ChassisMoveController coordinate frame
        # therefore if the line is left of frame, vector angle will be positive and robot will rotate anticlockwise
        delta_y = abs(centroid[1] - self._chassis_center_y)

        chassis_vector_angle = arctan(centroid[0] / delta_y) * 180 / pi

        return chassis_vector_angle

    def get_line_center(self):
        return

    @property
    def linear_speed(self):
        return self._chassis_controller.speed_linear_x

    @linear_speed.setter
    def linear_speed(self, speed):
        self._chassis_controller.speed_linear_x = speed

    def get_contour_bound_parameters(self):
        x, y, w, h = self._line_detector.contour_bound_scale_up()
        return x, y, w, h

    def stop_robot(self):
        self._chassis_controller.stop_chassis()

    def exit(self):
        cv2.destroyAllWindows()
        self._chassis_controller.stop_chassis()
