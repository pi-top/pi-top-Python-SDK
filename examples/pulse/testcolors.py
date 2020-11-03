#! /usr/bin/python3

# Test color representation of the pi-topPULSE led matrix
#
# Displays 49 different color intensities in the 49 pixels of the lex matrix
#
# by @rricharz
#
# Note:
# The hardware representation of each color is 5 bits e.g. only 32 different values
# Without gamma correction, this would mean the actual color value
# changes only every 8th color intensity value
# The pi-top library also applies a gamma correction
# Therefore multiple pixels have the same intensity
#

from ptpulse import ledmatrix
import time


def showMap(r, g, b):
    for x in range(0, 7):
        for y in range(0, 7):
            z = (float(y) + 7.0 * float(x)) / 49.0
            rr = int(z * r)
            gg = int(z * g)
            bb = int(z * b)
            # print(x,y,rr,gg,bb)
            ledmatrix.set_pixel(x, y, rr, gg, bb)
    ledmatrix.show()


ledmatrix.rotation(0)
ledmatrix.clear()

for r in range(0, 2):
    for g in range(0, 2):
        for b in range(2):
            if (r + g + b > 0):
                rr = 255 * r
                gg = 255 * g
                bb = 255 * b
                print(rr, gg, bb)
                showMap(rr, gg, bb)
                time.sleep(5)

ledmatrix.clear()
ledmatrix.show()
