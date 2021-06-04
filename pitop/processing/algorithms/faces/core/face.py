from pitop.processing.core.vision_functions import center_reposition
from .face_utils import (
    pupil_distance,
    get_face_angle,
    left_eye_center,
    left_eye_dimensions,
    right_eye_center,
    right_eye_dimensions,
    mouth_center,
    mouth_dimensions,
    nose_bottom,
)


class Face:
    def __init__(self):
        self._center = None
        self._features = None
        self._rectangle = None
        self._robot_view = None
        self._original_frame = None

    def clear(self):
        self.center_default = None
        self.features = None
        self.rectangle = None

    @property
    def center(self):
        """
        :return: Face center with the coordinate system in the middle of the frame.
                 Positive x points right, positive y points up.
        :type: tuple
        """
        return center_reposition(self.center_default, self.original_detection_frame) if self.found else None

    @property
    def center_default(self):
        """
        :return: Face center with the coordinate system in the top left of the frame.
                 Positive x points right, positive y points down. This is the same coordinate system used by OpenCV
                 and PIL.
        :type: tuple
        """
        return self._center

    @center_default.setter
    def center_default(self, value):
        self._center = value

    @property
    def angle(self):
        return get_face_angle(self.features) if self.found else None

    @property
    def pupil_distance(self):
        return pupil_distance(self.features) if self.found else None

    @property
    def left_eye_center(self):
        return left_eye_center(self.features) if self.found else None

    @property
    def left_eye_dimensions(self):
        return left_eye_dimensions(self.features) if self.found else None

    @property
    def right_eye_center(self):
        return right_eye_center(self.features) if self.found else None

    @property
    def right_eye_dimensions(self):
        return right_eye_dimensions(self.features) if self.found else None

    @property
    def mouth_center(self):
        return mouth_center(self.features) if self.found else None

    @property
    def mouth_dimensions(self):
        return mouth_dimensions(self.features) if self.found else None

    @property
    def nose_bottom(self):
        return nose_bottom(self.features) if self.found else None

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        self._features = value

    @property
    def rectangle(self):
        return self._rectangle

    @rectangle.setter
    def rectangle(self, value):
        self._rectangle = value

    @property
    def robot_view(self):
        return self._robot_view

    @robot_view.setter
    def robot_view(self, value):
        self._robot_view = value

    @property
    def original_detection_frame(self):
        return self._original_frame

    @original_detection_frame.setter
    def original_detection_frame(self, value):
        self._original_frame = value

    @property
    def found(self) -> bool:
        """
        :return: Boolean to determine if a face was found in the frame.
        :rtype: bool
        """
        return self.center_default is not None
