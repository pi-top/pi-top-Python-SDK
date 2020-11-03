from pitop.keyboard.keylistener import KeyPressListener
from time import sleep


def on_up_pressed():
    print("up pressed")


def on_up_released():
    print("up released")


def on_down_pressed():
    print("down pressed")


def on_down_released():
    print("down released")


def on_left_pressed():
    print("left pressed")


def on_left_released():
    print("left released")


def on_right_pressed():
    print("right pressed")


def on_right_released():
    print("right released")


key_listener_up = KeyPressListener("up")
key_listener_down = KeyPressListener("down")
key_listener_left = KeyPressListener("left")
key_listener_right = KeyPressListener("right")
key_listener_uppercase_z = KeyPressListener("Z")

# Methods will be called when key is pressed:

key_listener_up.when_pressed = on_up_pressed
key_listener_up.when_released = on_up_released
key_listener_down.when_pressed = on_down_pressed
key_listener_down.when_released = on_down_released
key_listener_left.when_pressed = on_left_pressed
key_listener_left.when_released = on_left_released
key_listener_right.when_pressed = on_right_pressed
key_listener_right.when_released = on_right_released

# Or alternatively you can "poll" for key presses:

while True:
    if key_listener_uppercase_z.is_pressed == True:
        print("Z pressed!")

    sleep(0.1)
