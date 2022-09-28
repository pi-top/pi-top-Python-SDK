from pitop.labs import RoverWebController

from pitop import Camera, DriveController, Pitop

rover = Pitop()
rover.add_component(DriveController())
rover.add_component(Camera())

rover_controller = RoverWebController(
    get_frame=rover.camera.get_frame,
    drive=rover.drive,
)

rover_controller.serve_forever()
