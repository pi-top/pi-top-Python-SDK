from time import sleep

from pitop import BlockPiRover, UltrasonicSensor

# Create a BlockPiRover, intended for use via Further's BlockPi coding
rover = BlockPiRover(left_motor="M3", right_motor="M0")

# Driving methods available directly without .drive access
speed = 50

# Linear method optional param hold not provided in BlockPi
rover.forward(speed)
sleep(1)

rover.backward(speed)
rover.left(speed)
sleep(1)

# Turning method optional param turn_radius not provided in BlockPi
rover.right(speed)
sleep(1)

# Stop and rotate
rover.stop()
# Rotate method optional param time_to_take not provided in BlockPi
rover.rotate(180)

# drive.robot_move is available as move
# Move method optional param turn_radius not provided in BlockPi
angular_speed = 10
rover.move(speed, angular_speed)
sleep(1)


# Advanced (not initially available via BlockPi)

# Use miniscreen display
rover.miniscreen.display_multiline_text("hey there!")

# Add other components
sensor = UltrasonicSensor("D3")
rover.add_component(sensor)
rover.ultrasonic.distance()
