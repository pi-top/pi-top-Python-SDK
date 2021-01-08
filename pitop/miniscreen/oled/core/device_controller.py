import atexit

from pitopcommon.lock import PTLock
from pitopcommon.ptdm import PTDMRequestClient, Message

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


class OledDeviceController:
    SPI_DEVICE = 0
    SPI_BUS_SPEED_HZ = 8000000
    SPI_TRANSFER_SIZE = 4096

    def __init__(self):
        self.__spi_bus = None
        self.__device = None
        self.__exclusive_mode = True
        self.lock = PTLock("pt-oled")

    def __set_controls(self, controlled_by_pi):
        message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, [str(int(controlled_by_pi))])

        with PTDMRequestClient() as request_client:
            request_client.send_message(message)

    def __setup_device(self):
        if self.__exclusive_mode:
            self.lock.acquire()
            atexit.register(self.reset_device)

        spi_port = self.spi_bus

        # Always use CE1
        if spi_port == 1:
            gpio_DC_pin = 17
        else:
            gpio_DC_pin = 7

        self.__device = sh1106(
            serial_interface=spi(
                port=spi_port,
                device=self.SPI_DEVICE,
                bus_speed_hz=self.SPI_BUS_SPEED_HZ,
                transfer_size=self.SPI_TRANSFER_SIZE,
                gpio_DC=gpio_DC_pin,
                gpio_RST=None,
                gpio=None,
            ),
            rotate=0
        )

    ##############################
    # Only intended to be used by pt-sys-oled
    ##############################

    def set_exclusive_mode(self, val: bool):
        self.__exclusive_mode = val
        self.reset_device()

    ##############################
    # Public methods
    ##############################

    def device_is_active(self):
        if (self.__exclusive_mode is True and self.__device is not None):
            # We already have the device, so no-one else can
            return False

        return self.lock.is_locked()

    def reset_device(self):
        self.__device = None
        if self.lock.is_locked():
            self.lock.release()

    def get_device(self):
        if self.__device is None:
            self.__setup_device()

        return self.__device

    def set_control_to_pi(self):
        self.__set_controls(controlled_by_pi=True)

    def set_control_to_hub(self):
        self.__set_controls(controlled_by_pi=False)

    @property
    def spi_bus(self):
        if self.__spi_bus is not None:
            return self.__spi_bus

        message = Message.from_parts(Message.REQ_GET_OLED_SPI_BUS)

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        self.__spi_bus = int(response.parameters[0])

        return self.__spi_bus

    @spi_bus.setter
    def spi_bus(self, bus):
        if self.__spi_bus == bus:
            return

        message = Message.from_parts(Message.REQ_SET_OLED_SPI_BUS, [str(bus)])

        with PTDMRequestClient() as request_client:
            request_client.send_message(message)
