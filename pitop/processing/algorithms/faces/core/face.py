from pitop.processing.core.vision_functions import center_reposition


class Face:
    def __init__(self):
        self._center = None
        self._features = None
        self._angle = None
        self._rectangle = None
        self._robot_view = None
        self._original_frame = None

    def clear(self):
        self.center = None
        self.features = None
        self.angle = None
        self.rectangle = None

    @property
    def center(self):
        return center_reposition(self._center, self.original_detection_frame) if self._center is not None else None

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def center_top_left_zero(self):
        return self._center

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

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
        return self.center is not None
