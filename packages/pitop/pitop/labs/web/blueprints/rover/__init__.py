from flask import Blueprint, g

from pitop.labs.web.blueprints.controller import ControllerBlueprint
from pitop.labs.web.utils import uses_flask_1

from .helpers import calculate_pan_tilt_angle, calculate_velocity_twist


def drive_handler(drive, data):
    velocity_twist = calculate_velocity_twist(data)
    linear = velocity_twist.get("linear", 0)
    angular = velocity_twist.get("angular", 0)

    drive.robot_move(linear, angular)


def pan_tilt_handler(pan_tilt, data):
    angle = calculate_pan_tilt_angle(data)

    pan_tilt.pan_servo.target_angle = angle.get("z")
    pan_tilt.tilt_servo.target_angle = angle.get("y")


class RoverControllerBlueprint(Blueprint):
    def __init__(
        self, drive=None, pan_tilt=None, get_frame=None, message_handlers=None, **kwargs
    ):
        message_handlers = {} if message_handlers is None else message_handlers
        Blueprint.__init__(
            self, "rover", __name__, template_folder="templates", **kwargs
        )

        passed_left_joystick_handler = message_handlers.get("left_joystick") is not None

        # set show_left_joystick every request for use in base-rover.html
        @self.before_app_request
        def set_show_left_joystick():
            g.show_left_joystick = passed_left_joystick_handler or pan_tilt is not None

        if message_handlers.get("left_joystick") is None:

            def left_joystick(data):
                return pan_tilt_handler(pan_tilt, data)

            message_handlers["left_joystick"] = left_joystick

        if message_handlers.get("right_joystick") is None:

            def right_joystick(data):
                return drive_handler(drive, data)

            message_handlers["right_joystick"] = right_joystick

        self.controller_blueprint = ControllerBlueprint(
            get_frame=get_frame, message_handlers=message_handlers
        )

    def register(self, app, options, *args, **kwargs):
        if uses_flask_1():
            app.register_blueprint(self.controller_blueprint, **options)
            Blueprint.register(self, app, options, *args, **kwargs)
        else:
            Blueprint.register(self, app, options, *args, **kwargs)
            app.register_blueprint(self.controller_blueprint, **options)

    def broadcast(self, message):
        self.controller_blueprint.broadcast(message)
