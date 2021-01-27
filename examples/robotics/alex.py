from pitop import AlexRobot

from time import sleep


# Setup robot
robot = AlexRobot()

# Use display
robot.oled.display_multiline_text("hi!\nI'm Alex!")

# Move it
robot.forward(0.5)
sleep(2)
robot.left(0.5)
sleep(2)
robot.backward(0.5)
sleep(2)
robot.right(0.5)
sleep(2)
