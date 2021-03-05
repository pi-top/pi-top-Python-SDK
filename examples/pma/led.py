from pitop import LED
from time import sleep

led = LED("D2")

led.on()
print(led.is_lit)
sleep(1)

led.off()
print(led.is_lit)
sleep(1)

led.toggle()
print(led.is_lit)
sleep(1)

print(led.value)  # Returns 1 is the led is on or 0 if the led is off
