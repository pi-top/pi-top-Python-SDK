from pitop.protoplus import DistanceSensor
from time import sleep

ultrasonic = DistanceSensor()

while True:
    print(ultrasonic.distance)
    sleep(1)
