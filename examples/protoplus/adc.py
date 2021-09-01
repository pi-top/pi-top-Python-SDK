from time import sleep

from pitop.protoplus import ADCProbe

temp_sensor = ADCProbe()

while True:
    print(temp_sensor.read_value(1))
    sleep(0.5)
