import atexit
from fcntl import ioctl, flock, LOCK_EX, LOCK_UN, LOCK_NB
from io import open as iopen
from os import path, chmod, environ

from pitop.core.sys_info import is_pi
from pitop.core.logger import PTLogger
from pitop.core.current_session_info import get_first_display


_device = None
_device_lock_handle = None
_device_lock_file = "/tmp/pt-oled.lock"
_exclusive_mode = True

# TODO: Read from hub via request client
spi_port = 1

# Always use CE1
if spi_port == 1:
    gpio_DC_pin = 17
else:
    gpio_DC_pin = 7

spi_device = 0
spi_bus_speed_hz = 8000000
spi_cs_high = False
spi_transfer_size = 4096


def _acquire_device_lock():
    global _device_lock_handle

    atexit.register(_release_device_lock)

    if device_reserved():
        raise IOError("Device already in use")

    _device_lock_handle = iopen(_device_lock_file, "w")
    try:
        chmod(_device_lock_file, 0o777)
    except:
        pass

    flock(_device_lock_handle, LOCK_EX)


def _release_device_lock():
    global _device_lock_handle

    if _device_lock_handle is not None:
        flock(_device_lock_handle.fileno(), LOCK_UN)
        _device_lock_handle.close()


def _setup_pi_and_get_device():
    import RPi.GPIO as GPIO

    # Suppress warning in Luma serial class
    GPIO.setwarnings(False)

    from luma.core.interface.serial import spi

    spi_serial_iface = spi(
        port=spi_port,
        device=spi_device,
        bus_speed_hz=spi_bus_speed_hz,
        cs_high=spi_cs_high,
        transfer_size=spi_transfer_size,
        gpio_DC=gpio_DC_pin,
        gpio_RST=None,
        gpio=None,
    )
    from luma.oled.device import sh1106

    return sh1106(serial_interface=spi_serial_iface, rotate=2)


def _setup_emulator_and_get_device():
    from luma.emulator.device import pygame

    first_display = get_first_display()
    if first_display is not None:
        environ["DISPLAY"] = first_display

    return pygame(
        height=64, mode="1", scale=4, transform="identity", width=128
    )

# Public methods ##############################


def device_reserved():

    if (_exclusive_mode is True and _device is not None):
        # We already have the device, so no-one else can
        return False

    temp_handle = None

    try:
        if (path.exists(_device_lock_file)):
            temp_handle = iopen(_device_lock_file, "w")
            flock(temp_handle, LOCK_EX | LOCK_NB)
            flock(temp_handle, LOCK_UN)
        return False
    except IOError:
        return True
    finally:
        if temp_handle is not None:
            temp_handle.close()


def reset_device_instance(emulator=None, exclusive=True):
    global _device

    del _device
    _device = None

    get_device_instance(emulator, exclusive)


def get_device_instance(emulator=None, exclusive=True):
    global _device, _exclusive_mode

    if _device is None:

        _exclusive_mode = exclusive
        if _exclusive_mode:
            _acquire_device_lock()

        if emulator is None:
            # Automatic detection
            _device = (
                _setup_pi_and_get_device()
                if is_pi()
                else _setup_emulator_and_get_device()
            )
        elif emulator is True:
            # Force emulator on
            _device = _setup_emulator_and_get_device()
        elif emulator is False:
            # Force emulator off
            _device = _setup_pi_and_get_device()

    return _device
