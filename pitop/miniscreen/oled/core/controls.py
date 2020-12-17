import atexit

from pitopcommon.ptdm import PTDMRequestClient, Message
from pitopcommon.lock import PTLock

from luma.core.interface.serial import spi
from luma.oled.device import sh1106

try:
    import RPi.GPIO as GPIO
    # Suppress warning in Luma serial class
    GPIO.setwarnings(False)
except RuntimeError:
    # This can only be run on Raspberry Pi
    # and is only required for reducing logging
    pass


_device = None
_exclusive_mode = True
lock = PTLock("pt-oled")

spi_device = 0
spi_bus_speed_hz = 8000000
spi_cs_high = False
spi_transfer_size = 4096


def __set_controls(controlled_by_pi):
    message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, [str(int(controlled_by_pi))])

    with PTDMRequestClient() as request_client:
        request_client.send_message(message)


def __setup_device():
    global _device

    if _exclusive_mode:
        lock.acquire()
        atexit.register(reset_device)

    spi_port = 1

    # Always use CE1
    if spi_port == 1:
        gpio_DC_pin = 17
    else:
        gpio_DC_pin = 7

    _device = sh1106(
        serial_interface=spi(
            port=spi_port,
            device=spi_device,
            bus_speed_hz=spi_bus_speed_hz,
            cs_high=spi_cs_high,
            transfer_size=spi_transfer_size,
            gpio_DC=gpio_DC_pin,
            gpio_RST=None,
            gpio=None,
        ),
        rotate=0
    )


##############################
# Only intended to be used by pt-sys-oled
##############################
def _set_exclusive_mode(val: bool):
    global _exclusive_mode
    _exclusive_mode = val
    reset_device()

##############################
# Public methods
##############################


def device_is_active():
    if (_exclusive_mode is True and _device is not None):
        # We already have the device, so no-one else can
        return False

    return lock.is_locked()


def reset_device():
    global _device
    _device = None
    if lock.is_locked():
        lock.release()


def get_device():
    if _device is None:
        __setup_device()

    return _device


def set_control_to_pi():
    __set_controls(controlled_by_pi=True)


def set_control_to_hub():
    __set_controls(controlled_by_pi=False)


##############################
# Deprecated methods
##############################
def get_device_instance():
    return get_device()


def device_reserved():
    return device_is_active()


def reset_device_instance():
    reset_device()
