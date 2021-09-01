from signal import pause
from time import sleep

from pitop import Pitop

pitop = Pitop()
display = pitop.display


# Get display information
print(f"Display brightness: {display.brightness}")
print(f"Display blanking timeout: {display.blanking_timeout}")
print(f"Display backlight is on: {display.backlight}")
print(f"Display lid is open: {display.lid_is_open}")

# Change the brightness levels incrementally
display.increment_brightness()
display.decrement_brightness()

# Set brightness explicitly
display.brightness = 7

# Set screen blank state
display.blank()
display.unblank()

# Set screen blanking timeout (s)
display.blanking_timeout = 60


# Define some functions to call on events
def do_brightness_changed_thing(new_brightness):
    print(new_brightness)
    print("Display brightness has changed!")


def do_screen_blanked_thing():
    print("Display is blanked!")


def do_screen_unblanked_thing():
    print("Display is unblanked!")


def do_lid_closed_thing():
    print("Display lid is closed!")


def do_lid_opened_thing():
    print("Display lid is open!")


# 'Wire up' functions to display events
display.when_brightness_changed = do_brightness_changed_thing
display.when_screen_blanked = do_screen_blanked_thing
display.when_screen_unblanked = do_screen_unblanked_thing
display.when_lid_closed = do_lid_closed_thing
display.when_lid_opened = do_lid_opened_thing


# Wait indefinitely for events to be handled in the background
pause()


# Or alternatively poll
print("Polling for if lid is open (Original pi-top/pi-top [3] only)")
while True:
    if display.lid_is_open:
        do_lid_opened_thing()
    sleep(0.1)
