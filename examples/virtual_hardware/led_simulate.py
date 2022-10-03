from pitop.virtual_hardware import simulate, use_virtual_hardware

use_virtual_hardware()

from time import sleep  # noqa: E402

from pitop import LED  # noqa: E402

green_led = LED("D2", color="green")

simulate(green_led)
while True:
    green_led.toggle()
    sleep(1)
