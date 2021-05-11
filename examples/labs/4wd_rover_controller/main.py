from pitop import Pitop, DriveController4WD, Camera, PanTiltController
from pitop.labs import RoverWebController
from pitop.labs.web.blueprints.rover.drive_handler_4wd import DriveMode, DriveHandler4WD

rover = Pitop()
rover.add_component(DriveController4WD())
rover.add_component(Camera(resolution=(320, 240)))
rover.add_component(PanTiltController())
rover.pan_tilt.calibrate()

drive_handler_4wd = DriveHandler4WD(drive=rover.drive, pan_tilt=rover.pan_tilt, mode=DriveMode.PAN_FOLLOW)

rover_controller = RoverWebController(
    get_frame=rover.camera.get_frame,
    message_handlers={
        'right_joystick': lambda data: drive_handler_4wd.right_joystick_update(data),
        'left_joystick': lambda data: drive_handler_4wd.left_joystick_update(data)
    }
)

rover_controller.serve_forever()
