from pitop import Button, LED
from time import sleep

button = Button("D1")
led = LED("D2")

# Connect button to LED
button.when_pressed = led.on
button.when_released = led.off

# Wait for Ctrl+C to exit
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    pass
