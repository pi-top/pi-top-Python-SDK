from time import sleep

from pitop import SoundSensor

sound_sensor = SoundSensor("A2")

while True:
    # Returns reading the amount of sound in the room
    print(sound_sensor.reading)
    sleep(0.1)
