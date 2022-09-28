from time import sleep

from pitop.robotics.drive_controller import DriveController

from pitop import LED, Pitop

pitop = Pitop()
drive_controller = DriveController()
led = LED("D0", name="red_led")

# Add components to the Pitop object
pitop.add_component(drive_controller)
pitop.add_component(led)

# Do something with the object
pitop.red_led.on()
pitop.drive.forward(0.5)
sleep(2)
pitop.red_led.off()
pitop.drive.stop()

# Store configuration to a file
pitop.save_config("/home/pi/my_custom_config.json")
