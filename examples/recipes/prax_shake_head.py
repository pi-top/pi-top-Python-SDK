from pitop import TiltRollHeadController
from time import sleep

# Create a head controller object
head = TiltRollHeadController()

# Initialize the servo angles
head.roll.target_angle = 0
head.tilt.target_angle = 50
sleep(1)


# Nod 6 times at max speed across a 5 degree angle. Block program execution until finished.
head.nod(times=6, angle=5, speed=100, block=True)

# Shake 6 times at half speed across a 10 degree angle. Block program execution until finished.
head.shake(times=6, angle=10, speed=50, block=True)

# Shake and nod at the same time with default speed and angle
# Setting nod with block=False ensures the program continues to the next command
head.nod(times=6, block=False)
head.shake(times=6, block=True)
