from pitop.pulse import configuration

from pitopcommon.logger import PTLogger

from copy import deepcopy
from math import (
    ceil,
    radians,
    sin,
    cos,
)
from os import path
from serial import (
    serialutil,
    Serial
)
import signal
from sys import exit
from time import sleep
from threading import Timer


_initialised = False

_w = 7
_h = 7
_rotation = 0
_brightness = 1.0

_max_freq = 50  # Maximum update speed is 50 times per second
_update_rate = 0.1

_running = False
_show_enabled = True

_gamma_correction_arr = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 2, 2, 2, 2, 2, 2, 2,
    2, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 5, 5, 5,
    5, 6, 6, 6, 6, 7, 7, 7,
    7, 8, 8, 8, 9, 9, 9, 10,
    10, 10, 11, 11, 11, 12, 12, 13,
    13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20,
    21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30,
    31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43,
    44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59,
    60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78,
    79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99, 101,
    102, 104, 105, 107, 109, 110, 112, 114,
    115, 117, 119, 120, 122, 124, 126, 127,
    129, 131, 133, 135, 137, 138, 140, 142,
    144, 146, 148, 150, 152, 154, 156, 158,
    160, 162, 164, 167, 169, 171, 173, 175,
    177, 180, 182, 184, 186, 189, 191, 193,
    196, 198, 200, 203, 205, 208, 210, 213,
    215, 218, 220, 223, 225, 228, 231, 233,
    236, 239, 241, 244, 247, 249, 252, 255
]

_sync = bytearray(
    [
        7,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127,
        127
    ]
)

_empty = [0, 0, 0]

_empty_map = [
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty],
    [_empty, _empty, _empty, _empty, _empty, _empty, _empty]
]

_pixel_map = deepcopy(_empty_map)

#######################
# INTERNAL OPERATIONS #
#######################


def __initialise():
    """INTERNAL. Initialise the matrix."""

    global _initialised
    global _serial_device
    global _pixel_map

    if not _initialised:
        if configuration.mcu_enabled():
            if not path.exists('/dev/serial0'):
                err_str = "Could not find serial port - are you sure it's enabled?"
                raise serialutil.SerialException(err_str)

            PTLogger.debug("Opening serial port...")

            _serial_device = Serial("/dev/serial0", baudrate=250000, timeout=2)

            if _serial_device.isOpen():
                PTLogger.debug("OK.")
            else:
                PTLogger.info("Error: Failed to open serial port!")
                exit()

            _initialised = True
        else:
            PTLogger.error("Error: pi-topPULSE not initialised by pt-device-manager")


def __signal_handler(signal, frame):
    """INTERNAL. Handles signals from the OS to exit."""

    PTLogger.info("\nQuitting...")

    stop()
    off()
    exit(0)


def __get_avg_colour():
    """INTERNAL. Get the average color of the matrix."""

    total_rgb = [0, 0, 0]
    avg_rgb = [0, 0, 0]

    for x in range(_w):
        for y in range(_h):
            for c in range(3):
                total_rgb[c] = total_rgb[c] + _pixel_map[x][y][c]

    for i, val in enumerate(total_rgb):
        avg_rgb[i] = int(round(val / (_w * _h)))

    return avg_rgb


def __write(data):
    """INTERNAL. Write data to the matrix."""

    PTLogger.debug('{s0:<4}{s1:<4}{s2:<4}{s3:<4}{s4:<4}{s5:<4}{s6:<4}{s7:<4}{s8:<4}{s9:<4}{s10:<4}'.format(
        s0=data[0], s1=data[1], s2=data[2], s3=data[3], s4=data[4], s5=data[5], s6=data[6], s7=data[7], s8=data[8], s9=data[9], s10=data[10]))
    _serial_device.write(data)
    sleep(0.002)


def __get_gamma_corrected_value(original_value):
    """INTERNAL. Converts a brightness value from 0-255
    to the value that produces an approximately linear
    scaling to the human eye."""

    return _gamma_correction_arr[original_value]


def __scale_pixel_to_brightness(original_value):
    """INTERNAL. Multiplies intended brightness of
    a pixel by brightness scaling factor to generate
    an adjusted value."""

    unrounded_new_brightness = original_value * _brightness
    rounded_new_brightness = round(unrounded_new_brightness)
    int_new_brightness = int(rounded_new_brightness)

    return int_new_brightness


def __get_rotated_pixel_map():
    """INTERNAL. Get a rotated copy of the current in-memory pixel map."""

    rotated_pixel_map = deepcopy(_pixel_map)

    # Some fancy maths to rotate pixel map so that
    # 0,0 (x,y) - with rotation 0 - is the bottom left LED
    scaled_rotation = int(_rotation / 90)
    adjusted_scaled_rotation = (scaled_rotation + 1)
    modulo_adjusted_scaled_rotation = (adjusted_scaled_rotation % 4)
    count = (6 - modulo_adjusted_scaled_rotation) % 4

    for x in range(count):
        rotated_pixel_map = list(zip(*rotated_pixel_map[::-1]))

    return rotated_pixel_map


def __brightness_correct(original_value):
    """INTERNAL. Correct a single color for brightness."""

    brightness_scaled = __scale_pixel_to_brightness(original_value)
    new_value = __get_gamma_corrected_value(brightness_scaled)

    return new_value


def __adjust_r_g_b_for_brightness_correction(r, g, b):
    """INTERNAL. Correct LED for brightness."""

    r = __brightness_correct(r)
    g = __brightness_correct(g)
    b = __brightness_correct(b)

    return r, g, b


def __sync_with_device():
    """INTERNAL. Send the sync frame to tell the device that LED
    data is expected."""

    __initialise()
    PTLogger.debug("Sync data:")
    __write(_sync)


def __rgb_to_bytes_to_send(rgb):
    """INTERNAL. Format the LED data in the device-specific layout."""

    # Create three 5-bit colour vals, splitting the green bits
    # into two parts (hardware spec):
    # |XX|G0|G1|R0|R1|R2|R3|R4|
    # |G2|G3|G4|B0|B1|B2|B3|B4|

    r = rgb[0]
    g = rgb[1]
    b = rgb[2]

    byte0 = (r >> 3) & 0x1F
    byte1 = (b >> 3) & 0x1F
    grnb0 = (g >> 1) & 0x60
    grnb1 = (g << 2) & 0xE0

    byte0 = (byte0 | grnb0) & 0xFF
    byte1 = (byte1 | grnb1) & 0xFF

    return byte0, byte1


def __timer_method():
    """INTERNAL. Run by the timer on each tick."""

    global _running
    global _update_rate

    while _running:
        show()
        sleep(_update_rate)


def __flip(direction):
    """INTERNAL. Flip the pixel map."""

    global _pixel_map

    flipped_pixel_map = deepcopy(_pixel_map)
    for x in range(_w):
        for y in range(_h):
            if direction == "h":
                flipped_pixel_map[x][y] = _pixel_map[(_w - 1) - x][y]
            elif direction == "v":
                flipped_pixel_map[x][y] = _pixel_map[x][(_h - 1) - y]
            else:
                err = 'Flip direction must be [h]orizontal or [v]ertical only'
                raise ValueError(err)

    _pixel_map = flipped_pixel_map


def __set_show_state(enabled):
    """INTERNAL."""

    global _show_enabled

    _show_enabled = enabled

    if not _show_enabled:
        _temp_disable_t.start()


def __enable_show_state():
    """INTERNAL."""

    __set_show_state(True)


def __disable_show_state():
    """INTERNAL."""

    __set_show_state(True)


#######################
# EXTERNAL OPERATIONS #
#######################

def set_debug_print_state(debug_enable):
    """Enable/disable debug prints"""

    global _debug
    _debug = debug_enable


def brightness(new_brightness):
    """Set the display brightness between 0.0 and 1.0.
        :param new_brightness: Brightness from 0.0 to 1.0 (default 1.0)"""

    global _brightness

    if new_brightness > 1 or new_brightness < 0:
        raise ValueError('Brightness level must be between 0 and 1')
    _brightness = new_brightness


def get_brightness():
    """Get the display brightness value. Returns a float between 0.0 and 1.0."""

    return _brightness


def rotation(new_rotation=0):
    """Set the display rotation.
    :param new_rotation: Specify the rotation in degrees: 0, 90, 180 or 270"""

    global _rotation

    if new_rotation in [0, 90, 180, 270]:
        _rotation = new_rotation
        return True
    else:
        raise ValueError('Rotation: 0, 90, 180 or 270 degrees only')


def flip_h():
    """Flips the grid horizontally."""

    __flip("h")


def flip_v():
    """Flips the grid vertically."""

    __flip("v")


def get_shape():
    """Returns the shape (width, height) of the display."""

    return (_w, _h)


def get_pixel(x, y):
    """Get the RGB value of a single pixel.
    :param x: Horizontal position from 0 to 7
    :param y: Veritcal position from 0 to 7"""

    global _pixel_map

    return _pixel_map[y][x]


def set_pixel(x, y, r, g, b):
    """Set a single pixel to RGB colour.
    :param x: Horizontal position from 0 to 7
    :param y: Veritcal position from 0 to 7
    :param r: Amount of red from 0 to 255
    :param g: Amount of green from 0 to 255
    :param b: Amount of blue from 0 to 255"""

    global _pixel_map

    new_r, new_g, new_b = __adjust_r_g_b_for_brightness_correction(r, g, b)
    _pixel_map[y][x] = [new_r, new_g, new_b]


def set_all(r, g, b):
    """Set all pixels to a specific colour."""

    global _pixel_map

    for x in range(_w):
        for y in range(_h):
            new_r, new_g, new_b = __adjust_r_g_b_for_brightness_correction(
                r, g, b)
            _pixel_map[x][y][0] = new_r
            _pixel_map[x][y][1] = new_g
            _pixel_map[x][y][2] = new_b


def show():
    """Update pi-topPULSE with the contents of the display buffer."""

    global _pixel_map
    global _rotation
    global _show_enabled

    wait_counter = 0

    attempt_to_show_early = not _show_enabled
    if attempt_to_show_early:
        PTLogger.info(
            "Can't update pi-topPULSE LEDs more than 50/s. Waiting...")

    pause_length = 0.001

    # Scale wait time to _max_freq
    wait_counter_length = ceil(float(1 / float(_max_freq * pause_length)))

    while not _show_enabled:
        if wait_counter >= wait_counter_length:
            # Timer hasn't reset for some reason - force override
            __enable_show_state()
            break
        else:
            sleep(pause_length)
            wait_counter = wait_counter + 1

    if attempt_to_show_early:
        PTLogger.debug("pi-topPULSE LEDs re-enabled.")

    __sync_with_device()

    rotated_pixel_map = __get_rotated_pixel_map()
    avg_rgb = __get_avg_colour()

    __initialise()

    PTLogger.debug("LED data:")
    # For each col
    for x in range(_w):
        # Write col to LED matrix
        # Start with col no., so LED matrix knows which one it belongs to
        pixel_map_buffer = chr(x)
        # Get col's frame buffer, iterating over each pixel
        for y in range(_h + 1):
            if y == _h:
                # Ambient lighting bytes
                byte0, byte1 = __rgb_to_bytes_to_send(avg_rgb)
            else:
                byte0, byte1 = __rgb_to_bytes_to_send(rotated_pixel_map[x][y])

            pixel_map_buffer += chr(byte0)
            pixel_map_buffer += chr(byte1)

        # Write col to LED matrix
        arr = bytearray(pixel_map_buffer, 'Latin_1')
        __write(arr)

        # Prevent another write if it's too fast
        __disable_show_state()


def clear():
    """Clear the buffer."""

    global _pixel_map

    _pixel_map = deepcopy(_empty_map)


def off():
    """Clear the buffer and immediately update pi-topPULSE."""

    clear()
    show()


def run_tests():
    """Runs a series of tests to check the LED board is working as expected."""

    off()

    # ------------------------------
    # Pixels
    # ------------------------------

    counter = 0

    for r in range(4):
        rotation(90 * r)
        for x in range(_w):
            for y in range(_h):
                rad = radians((float(counter) / (4 * _w * _h)) * 360)

                r = int((sin(rad) * 127) + 127)
                g = int((cos(rad) * 127) + 127)
                b = 255 - int((sin(rad) * 127) + 127)

                set_pixel(x, y, r, g, b)
                show()
                sleep(0.05)
                counter = counter + 1
        off()

    sleep(0.2)

    # ------------------------------
    # Rows and rotation
    # ------------------------------

    for r in range(4):
        rotation(90 * r)
        for c in range(3):
            for x in range(_w):
                for y in range(_h):
                    set_pixel(x, y, 255 if c == 0 else 0, 255 if c ==
                              1 else 0, 255 if c == 2 else 0)

                show()
                sleep(0.05)

    off()
    sleep(0.2)

    # ------------------------------
    # Brightness
    # ------------------------------

    for b in range(100):
        brightness(float(b) / 100)
        set_all(255, 255, 255)
        show()
        sleep(0.01)

    for b in range(100):
        brightness(1 - (float(b) / 100))
        set_all(255, 255, 255)
        show()
        sleep(0.01)

    off()
    brightness(1.0)

    sleep(0.2)

    # ------------------------------
    # Flipping
    # ------------------------------

    for x in range(int(_w / 2)):
        for y in range(int(_h / 2)):
            set_pixel(x, y, 255, 255, 255)

    set_pixel(int(_w / 4), int(_h / 4), 0, 255, 0)

    show()
    sleep(0.5)

    for f in range(4):
        for x in range(2):
            if x == 0:
                flip_h()
            else:
                flip_v()
            show()
            sleep(0.5)

    off()
    sleep(0.2)

    # ------------------------------
    # Conway - auto refresh
    # ------------------------------

    start(0.1)

    life_map = [[0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]]

    for r in range(40):
        temp_map = deepcopy(life_map)
        for x in range(_w):
            for y in range(_h):

                current_cell = temp_map[x][y]
                neighbours = 0
                neighbours = neighbours + temp_map[(x - 1) % _w][(y - 1) % _h]
                neighbours = neighbours + temp_map[(x - 1) % _w][(y - 0) % _h]
                neighbours = neighbours + temp_map[(x - 1) % _w][(y + 1) % _h]
                neighbours = neighbours + temp_map[(x - 0) % _w][(y - 1) % _h]
                neighbours = neighbours + temp_map[(x - 0) % _w][(y + 1) % _h]
                neighbours = neighbours + temp_map[(x + 1) % _w][(y - 1) % _h]
                neighbours = neighbours + temp_map[(x + 1) % _w][(y - 0) % _h]
                neighbours = neighbours + temp_map[(x + 1) % _w][(y + 1) % _h]

                if current_cell == 1 and (neighbours < 2 or neighbours > 3):
                    life_map[x][y] = 0

                if (current_cell == 0 and neighbours == 3):
                    life_map[x][y] = 1

        for x in range(_w):
            for y in range(_h):
                if (life_map[x][y] == 1):
                    set_pixel(x, y, 255, 255, 0)
                else:
                    set_pixel(x, y, 0, 128, 0)

        sleep(0.1)

    stop()
    off()


def start(new_update_rate=0.1):
    """Starts a timer to automatically refresh the LEDs."""

    global _update_rate
    global _running
    global _auto_refresh_timer

    if new_update_rate < (1 / _max_freq):
        _update_rate = (1 / _max_freq)
    else:
        _update_rate = new_update_rate

    _running = True
    _auto_refresh_timer.start()


def stop():
    """Stops the timer that automatically refreshes the LEDs."""

    global _running
    global _auto_refresh_timer

    _running = False
    _auto_refresh_timer.cancel()


##################
# INITIALISATION #
##################

_signal = signal.signal(signal.SIGINT, __signal_handler)
_auto_refresh_timer = Timer(_update_rate, __timer_method)
_temp_disable_t = Timer(_max_freq, __enable_show_state)

clear()
