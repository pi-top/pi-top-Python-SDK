from time import sleep

from pitop import TiltRollHeadController

# Create a head controller object
head = TiltRollHeadController()

# Initialize the servo angles
head.roll.target_angle = 0
head.tilt.target_angle = 50
sleep(1)


# Nod 6 times at max speed 5 degrees either side of current angle. Blocks program execution until finished.
head.nod(times=6, angle=5, speed=100, block=True)

# Shake 4 times at half speed 10 degrees either side of current angle. Blocks program execution until finished.
head.shake(times=4, angle=10, speed=50, block=True)

# Shake and nod at the same time with default speed and angle
# Setting nod with block=False ensures the program continues to the next command
head.nod(times=6, block=False)
head.shake(times=6, block=True)
