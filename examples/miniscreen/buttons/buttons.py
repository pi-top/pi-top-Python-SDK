from pitop.miniscreen import Miniscreen


miniscreen = Miniscreen()
up = miniscreen.up_button
down = miniscreen.down_button


def do_up_thing():
    print("Up button was pressed")


def do_down_thing():
    print("Down button was pressed")


def do_another_thing():
    print("do_another_thing invoked")


def select_something():
    print("select_something called")


# To invoke a function when the button is pressed/released,
# you can assign the function to the 'when_pressed' or 'when_released' data member of a button
up.when_pressed = do_up_thing
down.when_pressed = do_down_thing
down.when_released = do_another_thing


# Another way to react to button events is to poll the is_pressed data member
while True:
    if miniscreen.select_button.is_pressed:
        select_something()
