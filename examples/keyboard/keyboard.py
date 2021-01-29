from pitop.keyboard import KeyboardButton
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


keyboard_btn_up = KeyboardButton("up")
keyboard_btn_down = KeyboardButton("down")
keyboard_btn_left = KeyboardButton("left")
keyboard_btn_right = KeyboardButton("right")
keyboard_btn_uppercase_z = KeyboardButton("Z")

# Methods will be called when key is pressed:

keyboard_btn_up.when_pressed = on_up_pressed
keyboard_btn_up.when_released = on_up_released
keyboard_btn_down.when_pressed = on_down_pressed
keyboard_btn_down.when_released = on_down_released
keyboard_btn_left.when_pressed = on_left_pressed
keyboard_btn_left.when_released = on_left_released
keyboard_btn_right.when_pressed = on_right_pressed
keyboard_btn_right.when_released = on_right_released

# Or alternatively you can "poll" for key presses:

while True:
    if keyboard_btn_uppercase_z.is_pressed is True:
        print("Z pressed!")

    sleep(0.1)
