from pitop.pulse import ledmatrix
import time


def show_map(r, g, b):
    for x in range(0, 7):
        for y in range(0, 7):
            z = (float(y) + 7.0 * float(x)) / 49.0
            rr = int(z * r)
            gg = int(z * g)
            bb = int(z * b)
            ledmatrix.set_pixel(x, y, rr, gg, bb)
    ledmatrix.show()


ledmatrix.rotation(0)
ledmatrix.clear()

# Display 49 different color intensities
for r in range(0, 2):
    for g in range(0, 2):
        for b in range(2):
            if (r + g + b > 0):
                rr = 255 * r
                gg = 255 * g
                bb = 255 * b
                print(rr, gg, bb)
                show_map(rr, gg, bb)
                time.sleep(5)

ledmatrix.clear()
ledmatrix.show()
