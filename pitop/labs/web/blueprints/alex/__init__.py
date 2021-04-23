from pitop.labs.web.blueprints.controller import ControllerBlueprint

from flask import Blueprint
import math


def get_joystick_angle_scalers(data):
    angle = data.get('angle', {})
    degree = angle.get('degree', 0)
    distance = data.get('distance', 0)

    direction = degree - 90

    # 0:360 --> -180:180
    if direction > 180:
        direction = direction - 360

    return (
        -math.cos(direction / 57.29) * distance / 100.0,
        math.sin(direction / 57.29) * distance / 100.0,
    )


class RobotDriveControllerBlueprint(Blueprint):
    def __init__(
        self,
        video_feed=None,
        left_joystick=None,
        right_joystick=None,
        message_handlers={},
        **kwargs
    ):
        Blueprint.__init__(
            self,
            "alex",
            __name__,
            template_folder="templates",
            **kwargs
        )

        self.left_joystick_func = left_joystick
        self.right_joystick_func = right_joystick

        if message_handlers.get('left_joystick') is None:
            message_handlers['left_joystick'] = self.left_joystick

        if message_handlers.get('right_joystick') is None:
            message_handlers['right_joystick'] = self.right_joystick

        self.controller_blueprint = ControllerBlueprint(
            video_feed=video_feed, message_handlers=message_handlers)

    def register(self, app, options, *args, **kwargs):
        app.register_blueprint(self.controller_blueprint, **options)
        Blueprint.register(self, app, options, *args, **kwargs)

    def left_joystick(self, data):
        # Called by message handler
        self.left_joystick_func(*get_joystick_angle_scalers(data))

    def right_joystick(self, data):
        # Called by message handler
        self.right_joystick_func(*get_joystick_angle_scalers(data))
