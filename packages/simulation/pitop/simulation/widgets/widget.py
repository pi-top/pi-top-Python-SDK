from abc import ABC, abstractmethod


class WidgetBase(ABC):
    def __init__(self, x, y, width, height):
        """Base for all widgets.

        :param x: X-coordinate of top left
        :type x: int
        :param y: Y-coordinate of top left
        :type y: int
        :param width: Width of button
        :type width: int
        :param height: Height of button
        :type height: int
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._hidden = False
        self._disabled = False

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def __repr__(self):
        return f"{type(self).__name__}(x = {self.x}, y = {self.y}, width = {self.width}, height = {self.height})"

    def hide(self):
        self._hidden = True

    def show(self):
        self._hidden = False

    def disable(self):
        self._disabled = True

    def enable(self):
        self._disabled = False

    def moveX(self, x):
        self.x += x

    def moveY(self, y):
        self.y += y

    def get(self, attr):
        """Default setter for any attributes. Call super if overriding.

        :param attr: Attribute to get
        :return: Value of the attribute
        """
        if attr == "x":
            return self.x

        if attr == "y":
            return self.y

        if attr == "width":
            return self.width

        if attr == "height":
            return self.height

    def isVisible(self):
        return not self._hidden

    def isEnabled(self):
        return not self._disabled

    def set(self, attr, value):
        """Default setter for any attributes. Call super if overriding.

        :param attr: Attribute to set
        :param value: Value to set
        """
        if attr == "x":
            self.x = value

        if attr == "y":
            self.y = value

        if attr == "width":
            self.width = value

        if attr == "height":
            self.height = value
