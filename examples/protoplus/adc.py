from pitop.protoplus import ADCProbe
from time import sleep


temp_sensor = ADCProbe()

while True:
    print(temp_sensor.read_value(1))
    sleep(0.5)
