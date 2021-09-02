from time import sleep

from pitop import LightSensor

light_sensor = LightSensor("A1")

while True:
    # Returns a value depending on the amount of light
    print(light_sensor.reading)
    sleep(0.1)
