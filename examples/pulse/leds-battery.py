from pitop.pulse import ledmatrix
from pitop.battery import Battery

from time import sleep


def draw_battery_outline():  # Draw the naked battery
    for y in range(0, 6):
        ledmatrix.set_pixel(1, y, 64, 64, 255)
        ledmatrix.set_pixel(5, y, 64, 64, 255)
    for x in range(2, 5):
        ledmatrix.set_pixel(x, 0, 64, 64, 255)
        ledmatrix.set_pixel(x, 6, 192, 192, 192)
    ledmatrix.show()


def update_battery_state(charging_state, capacity):
    r = 0
    g = 0
    b = 0
    if charging_state == 0:
        if capacity < 11:
            r = 255
        else:
            g = 255
    elif charging_state == 1:
        r = 255
        g = 225

    cap = int(capacity / 20) + 1
    if cap < 0:
        cap = 0
    if cap > 5:
        cap = 5

    if cap > 0:
        for y in range(1, cap+1):
            ledmatrix.set_pixel(2, y, r, g, b)
            ledmatrix.set_pixel(3, y, r, g, b)
            ledmatrix.set_pixel(4, y, r, g, b)
    if cap == 0:
        cap = 1
    if cap < 6:
        if (capacity < 50) and (charging_state == 0):
            # blinking warning
            for i in range(1, 3):
                for y in range(cap+1, 6):
                    ledmatrix.set_pixel(2, y, 0, 0, 0)
                    ledmatrix.set_pixel(3, y, 0, 0, 0)
                    ledmatrix.set_pixel(4, y, 0, 0, 0)
                ledmatrix.show()
                sleep(0.4)
                for y in range(cap+1, 6):
                    ledmatrix.set_pixel(2, y, 255, 0, 0)
                    ledmatrix.set_pixel(3, y, 255, 0, 0)
                    ledmatrix.set_pixel(4, y, 255, 0, 0)
                ledmatrix.show()
                sleep(0.4)

        else:
            for y in range(cap+1, 6):
                ledmatrix.set_pixel(2, y, 0, 0, 0)
                ledmatrix.set_pixel(3, y, 0, 0, 0)
                ledmatrix.set_pixel(4, y, 0, 0, 0)
            ledmatrix.show()
            sleep(5)
    return 0


def main():
    ledmatrix.rotation(0)
    ledmatrix.clear()          # Clear the display
    draw_battery_outline()     # Draw the battery outline

    while True:
        try:
            charging_state, capacity, _, _ = Battery.get_full_state()
            update_battery_state(charging_state, capacity)  # Fill battery with capacity

        except Exception as e:
            print("Error getting battery info: " + str(e))


if __name__ == "__main__":
    main()
