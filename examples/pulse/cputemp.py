#! /usr/bin/python3

# Display the cpu temperature in degree C on the pi-topPULSE led matrix
#
# based on the script to display digits on the sense hat
# by yaab-arduino.blogspot.ch
# adapted for the pi-topPULSE by @rricharz
# cpu temperature code added by @rricharz
#

from ptpulse import ledmatrix
import time
import os


def getCpuTemperature():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return int(int(cpu_temp) / 1000)


OFFSET_LEFT = 0
OFFSET_TOP = 2

NUMS = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1,  # 0
        0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0,  # 1
        1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1,  # 2
        1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1,  # 3
        1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1,  # 4
        1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1,  # 5
        1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1,  # 6
        1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0,  # 7
        1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1,  # 8
        1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1]  # 9


# Displays a single digit (0-9)
def show_digit(val, xd, yd, r, g, b):
    offset = val * 15
    for p in range(offset, offset + 15):
        xt = p % 3
        yt = (p-offset) // 3
        ledmatrix.set_pixel(xt+xd, 7-yt-yd, r*NUMS[p], g*NUMS[p], b*NUMS[p])
    ledmatrix.show()


# Displays a two-digits positive number (0-99)
def show_number(val, r, g, b):
    abs_val = abs(val)
    tens = abs_val // 10
    units = abs_val % 10
    if (abs_val > 9):
        show_digit(tens, OFFSET_LEFT, OFFSET_TOP, r, g, b)
    show_digit(units, OFFSET_LEFT+4, OFFSET_TOP, r, g, b)


###########################################################
# MAIN
###########################################################

ledmatrix.rotation(0)
ledmatrix.clear()

lastTemperature = -1

while True:
    temperature = getCpuTemperature()
    if temperature != lastTemperature:
        if temperature < 60:
            show_number(temperature, 0, 255, 0)
        elif temperature < 70:
            show_number(temperature, 255, 255, 0)
        else:
            show_number(temperature, 255, 0, 0)
        lastemperature = temperature
    time.sleep(2)

ledmatrix.clear()
ledmatrix.show()
