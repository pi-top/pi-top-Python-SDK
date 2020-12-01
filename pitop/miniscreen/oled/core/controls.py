import atexit

from pitopcommon.ptdm_request_client import PTDMRequestClient
from pitopcommon.ptdm_message import Message
from pitopcommon.lock import PTLock

import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.oled.device import sh1106


# Suppress warning in Luma serial class
GPIO.setwarnings(False)

_device = None
_exclusive_mode = True
lock = PTLock("pt-oled")

spi_device = 0
spi_bus_speed_hz = 8000000
spi_cs_high = False
spi_transfer_size = 4096


class MiniScreenOLEDManagerException(Exception):
    pass


def __set_controls(controlled_by_pi):
    message = Message.from_parts(Message.REQ_SET_CONTROL, [str(int(controlled_by_pi))])

    with PTDMRequestClient() as request_client:
        response = request_client.send_message(message)

    if response.message_id() != Message.RSP_SET_CONTROL:
        target_str = "Raspberry Pi" if controlled_by_pi else "pi-top hub"
        raise MiniScreenOLEDManagerException(
            f"Unable to give control of OLED to {target_str}"
        )


def __setup_device():
    global _device

    if _exclusive_mode:
        lock.acquire()
        atexit.register(lock.release())

    # TODO: Read from hub via request client
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
        rotate=2
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
