
from pitop.virtual_hardware import simulate, use_virtual_hardware

use_virtual_hardware()

from time import sleep
from pitop import LED

green_led = LED("D2", color="green")

simulate(green_led)
while True:
    green_led.toggle()
    sleep(1)
