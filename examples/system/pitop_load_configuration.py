from time import sleep

from pitop import Pitop

# Load configuration from a previous session
pitop = Pitop.from_file("/home/pi/my_custom_config.json")

# Check the loaded configuration
print(pitop.config)

# Do something with your device
pitop.red_led.on()
pitop.drive.forward(0.5)
sleep(2)
pitop.red_led.off()
pitop.drive.stop()

# Check the state of all the components attached to the Pitop object
print(pitop.component_state)
