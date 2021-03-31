from pitop import AlexRobot
from pitop.labs.webserver import run_webserver

alex = AlexRobot()
alex.calibrate()
alex.pan_servo.target_angle = 0
alex.tilt_servo.target_angle = 0

run_webserver(robot_instance=alex,
              port=8070,
              serve_forever=True)
