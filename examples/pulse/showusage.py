#! /usr/bin/python3

# Display the cpu usage of the 4 cores on the pi-topPULSE led matrix
#
# for Raspberry Pi 3
#
# by @rricharz

from ptpulse import ledmatrix
import time

lastWork = [0, 0, 0, 0]
lastIdle = [0, 0, 0, 0]


def getCpuRates():
    global lastWork, lastIdle
    rate = [0, 0, 0, 0]
    f = open("/proc/stat", "r")
    line = ""
    for i in range(0, 4):
        while not "cpu"+str(i) in line:
            line = f.readline()
        # print(line)
        splitline = line.split()
        work = int(splitline[1]) + int(splitline[2]) + int(splitline[3])
        idle = int(splitline[4])
        diffWork = work - lastWork[i]
        diffIdle = idle - lastIdle[i]
        rate[i] = float(diffWork) / float(diffIdle+diffWork)
        lastWork[i] = work
        lastIdle[i] = idle
    f.close()
    return rate


ledmatrix.rotation(0)
while True:
    rate = getCpuRates()
    ledmatrix.clear()
    for i in range(0, 4):
        level = int(6.99 * rate[i])
        if level < 4:
            r = 0
            g = 255
            b = 0
        elif level < 6:
            r = 255
            g = 255
            b = 6
        else:
            r = 255
            g = 0
            b = 0
        for y in range(0, level+1):
            ledmatrix.set_pixel(2 * i, y, r, g, b)

    ledmatrix.show()
    time.sleep(1)


ledmatrix.clear()
ledmatrix.show()
