from pitop import Button
from time import sleep

button = Button("D5")

def on_button_pressed():
    print("Pressed!")


def on_button_released():
    print("Released!")


button.when_pressed = on_button_pressed
button.when_released = on_button_released

while True:
    if button.is_pressed is True:  # When button is pressed it will return True
        print(button.value)
    sleep(1)
