from pitop import Pitop, DriveController4WD, Camera
from pitop.labs import RoverWebController
from pitop.labs.web.blueprints.rover import DriveHandler4WD

rover = Pitop()
rover.add_component(DriveController4WD())
rover.add_component(Camera(resolution=(320, 240)))

drive_handler_4wd = DriveHandler4WD(drive=rover.drive)

rover_controller = RoverWebController(
    get_frame=rover.camera.get_frame,
    message_handlers={
        'right_joystick': lambda data: drive_handler_4wd.update_linear(data),
        'left_joystick': lambda data: drive_handler_4wd.update_angular(data)
    }
)

rover_controller.serve_forever()
