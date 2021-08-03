class Emotion:
    def __init__(self):
        self._type = None
        self._confidence = 0.0
        self._robot_view = None

    def clear(self):
        self.type = None
        self.confidence = 0.0

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def confidence(self):
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        self._confidence = value

    @property
    def robot_view(self):
        return self._robot_view

    @robot_view.setter
    def robot_view(self, value):
        self._robot_view = value

    @property
    def found(self):
        return self.type is not None
