from pitop.pulse import ledmatrix

import time

last_work = [0, 0, 0, 0]
last_idle = [0, 0, 0, 0]


def get_cpu_rates():
    global last_work, last_idle
    rate = [0, 0, 0, 0]
    f = open("/proc/stat", "r")
    line = ""
    for i in range(0, 4):
        while not "cpu" + str(i) in line:
            line = f.readline()
        # print(line)
        splitline = line.split()
        work = int(splitline[1]) + int(splitline[2]) + int(splitline[3])
        idle = int(splitline[4])
        diff_work = work - last_work[i]
        diff_idle = idle - last_idle[i]
        rate[i] = float(diff_work) / float(diff_idle + diff_work)
        last_work[i] = work
        last_idle[i] = idle
    f.close()
    return rate


ledmatrix.rotation(0)

try:
    while True:
        rate = get_cpu_rates()
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
            for y in range(0, level + 1):
                ledmatrix.set_pixel(2 * i, y, r, g, b)

        ledmatrix.show()
        time.sleep(1)

except KeyboardInterrupt:
    ledmatrix.clear()
    ledmatrix.show()
