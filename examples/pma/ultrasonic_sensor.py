from time import sleep

from pitop import UltrasonicSensor

distance_sensor = UltrasonicSensor("D3", threshold_distance=0.2)

# Set up functions to print when an object crosses 'threshold_distance'
distance_sensor.when_in_range = lambda: print("in range")
distance_sensor.when_out_of_range = lambda: print("out of range")

while True:
    # Print the distance (in meters) to an object in front of the sensor
    print(distance_sensor.distance)
    sleep(0.1)
