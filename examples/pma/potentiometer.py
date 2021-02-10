from pitop import Potentiometer
from time import sleep

potentiometer = Potentiometer("A3")

while True:
    # Returns the current position of the Potentiometer
    print(potentiometer.position)
    sleep(0.1)
