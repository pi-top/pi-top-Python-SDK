from pitop import AlexRobot

from time import sleep


# Set up Alex
alex = AlexRobot()

# Use miniscreen display
alex.miniscreen.display_multiline_text("hi!\nI'm Alex!")

# Move it
alex.forward(0.5)
sleep(2)
alex.left(0.5)
sleep(2)
alex.backward(0.5)
sleep(2)
alex.right(0.5)
sleep(2)
