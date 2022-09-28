from pitop.labs import RoverWebController
from pitop.labs.web.blueprints.rover import drive_handler, pan_tilt_handler

from pitop import Camera, DriveController, PanTiltController, Pitop

rover = Pitop()
rover.add_component(DriveController())
rover.add_component(PanTiltController())
rover.add_component(Camera())

rover_controller = RoverWebController(
    get_frame=rover.camera.get_frame,
    message_handlers={
        "left_joystick": lambda data: drive_handler(rover.drive, data),
        "right_joystick": lambda data: pan_tilt_handler(rover.pan_tilt, data),
    },
)

rover_controller.serve_forever()
