from pitop import Buzzer
from time import sleep

buzzer = Buzzer("D0")

buzzer.on()  # Set buzzer sound on
print(buzzer.value)  # Return 1 while the buzzer is on
sleep(2)

buzzer.off()  # Set buzzer sound off
print(buzzer.value)  # Return 0 while the buzzer is off
sleep(2)

buzzer.toggle()  # Swap between on and off states
print(buzzer.value)  # Return the current state of the buzzer

sleep(2)

buzzer.off()
