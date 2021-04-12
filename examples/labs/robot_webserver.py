from pitop import Pitop, DriveController, PanTiltController, Camera
from pitop.labs.webserver import run_webserver


# Create components
robot = Pitop()
drive_controller = DriveController()
pan_tilt = PanTiltController()
camera = Camera()


# Add components to the robot object
robot.add_component(drive_controller)
robot.add_component(pan_tilt)
robot.add_component(camera)


# Run webserver
run_webserver(robot_instance=robot,
              port=8070,
              serve_forever=True)
