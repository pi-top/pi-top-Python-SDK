from pitop import Pitop
from pitop.pma import LED, Button
from time import sleep

pitop = Pitop()
pitop.add_component(LED("D0"))
pitop.add_component(Button("D1"))

pitop.button.when_pressed = pitop.led.on
pitop.button.when_released = pitop.led.off

pitop.simulate()
while True:
    sleep(0.1)
