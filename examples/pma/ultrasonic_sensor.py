from pitop.pma import UltrasonicSensor
from time import sleep

distance_sensor = UltrasonicSensor("D3")
while True:
    # Returns reading of the distance in meters how far an object is in front of the sensor
    print(distance_sensor.distance)
    sleep(0.1)
