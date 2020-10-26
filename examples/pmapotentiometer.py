from ptpma import PMAPotentiometer
from time import sleep

potentiometer = PMAPotentiometer("A3")

while True:
    # Returns the current position of the Potentiometer
    print(potentiometer.position)
    sleep(0.1)
