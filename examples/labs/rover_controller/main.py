from pitop import DriveController, Camera
from pitop.labs import RoverWebController

drive = DriveController()
camera = Camera()

rover_controller = RoverWebController(
    get_frame=camera.get_frame,
    drive=drive,
)

rover_controller.serve_forever()
