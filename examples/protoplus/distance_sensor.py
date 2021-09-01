from time import sleep

from pitop.protoplus import DistanceSensor

ultrasonic = DistanceSensor()

while True:
    print(ultrasonic.distance)
    sleep(1)
