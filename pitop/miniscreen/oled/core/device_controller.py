import atexit

from pitopcommon.lock import PTLock
from pitopcommon.ptdm import (
    Message,
    PTDMRequestClient,
    PTDMSubscribeClient,
)

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
        self.__spi_bus = self.__get_spi_bus_from_ptdm()
        self.__device = None
        self.__exclusive_mode = True
        self.lock = PTLock("pt-oled")

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def on_spi_bus_changed(parameters):
            self.__spi_bus = int(parameters[0])
            self.reset_device()

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise({
            Message.PUB_OLED_SPI_BUS_CHANGED: on_spi_bus_changed
        })
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    def __set_controls(self, controlled_by_pi):
        message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, [str(int(controlled_by_pi))])

        with PTDMRequestClient() as request_client:
            request_client.send_message(message)

    def __setup_device(self):
        if self.__exclusive_mode:
            self.lock.acquire()
            atexit.register(self.reset_device)

        self.__device = sh1106(
            serial_interface=spi(
                port=self.__spi_bus,
                device=self.SPI_DEVICE,
                bus_speed_hz=self.SPI_BUS_SPEED_HZ,
                transfer_size=self.SPI_TRANSFER_SIZE,
                gpio_DC=17 if self.__spi_bus == 1 else 7,  # Always use CE1
                gpio_RST=None,
                gpio=None,
            ),
            rotate=0
        )

    def __get_spi_bus_from_ptdm(self):
        message = Message.from_parts(Message.REQ_GET_OLED_SPI_BUS)

        with PTDMRequestClient() as request_client:
            response = request_client.send_message(message)

        return int(response.parameters[0])

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
        return self.__spi_bus

    @spi_bus.setter
    def spi_bus(self, bus):
        '''
        Request SPI bus change from pi-top device manager
        '''
        assert bus in range(0, 1)

        if self.__spi_bus == bus:
            return

        message = Message.from_parts(Message.REQ_SET_OLED_SPI_BUS, [str(bus)])

        with PTDMRequestClient() as request_client:
            request_client.send_message(message)

        # Wait for publish event from ptdm to update.
        #
        # Internal state of SPI bus is handled via subscribe client.
        # When the subscribe client receives an SPI bus change event,
        # the device manager has finished configuration. The response
        # received here simply shows that it has acknowledged the request.
