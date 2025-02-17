from time import sleep

from pitop.robotics import DriveController

drive = DriveController(left_motor_port="M3", right_motor_port="M0")

# Move forward
drive.forward(speed_factor=0.3)

# If a distance is not provided, the robot will move indefinitely
# Let it move for 1 second before stopping
sleep(1)
drive.stop()

# Rotate in place 180 degrees
drive.rotate(angle=180)

# Move to the right, following a curve for 10 centimeters
drive.right(speed_factor=0.5, turn_radius=0.5, distance=0.1)

# Move backward
drive.backward(speed_factor=0.5, distance=0.1)
