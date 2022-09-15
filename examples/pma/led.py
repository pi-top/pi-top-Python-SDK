from time import sleep

from pitop import LED

led = LED("D0")
green_led = LED("D2", color="green")

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
led.simulate()
sleep(5)
green_led.simulate()
while True:
    led.toggle()
    green_led.toggle()
    sleep(1)
