"""Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bit-banging GPIO."""

import errno
from time import sleep

import RPi.GPIO as GPIO
from spidev import SpiDev

from pitop.miniscreen.oled.core.contrib.luma.core.error import DeviceNotFoundError

GPIO.setmode(GPIO.BCM)
# Suppress serial warnings
GPIO.setwarnings(False)


class bitbang(object):
    """
    Wraps an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus to provide :py:func:`data` and
    :py:func:`command` methods. This is a software implementation and is thus
    a lot slower than the default SPI interface. Don't use this class directly
    unless there is a good reason!

    :param transfer_size: Max bytes to transfer in one go. Some implementations
        only support maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param reset_hold_time: The number of seconds to hold reset active. Some devices may require
        a duration of 100ms or more to fully reset the display (default:0)
    :type reset_hold_time: float
    :param reset_release_time: The number of seconds to delay afer reset. Some devices may require
        a duration of 150ms or more after reset was triggered before the device can accept the
        initialization sequence (default:0)
    :type reset_release_time: float
    :param SCLK: The GPIO pin to connect the SPI clock to.
    :type SCLK: int
    :param SDA: The GPIO pin to connect the SPI data (MOSI) line to.
    :type SDA: int
    :param CE: The GPIO pin to connect the SPI chip enable (CE) line to.
    :type CE: int
    :param DC: The GPIO pin to connect data/command select (DC) to.
    :type DC: int
    :param RST: The GPIO pin to connect reset (RES / RST) to.
    :type RST: int
    """

    def __init__(self, transfer_size=4096, reset_hold_time=0, reset_release_time=0, **kwargs):

        self._transfer_size = transfer_size

        self._SCLK = self._configure(kwargs.get("SCLK"))
        self._SDA = self._configure(kwargs.get("SDA"))
        self._CE = self._configure(kwargs.get("CE"))
        self._DC = self._configure(kwargs.get("DC"))
        self._RST = self._configure(kwargs.get("RST"))
        self._cmd_mode = GPIO.LOW  # Command mode = Hold low
        self._data_mode = GPIO.HIGH  # Data mode = Pull high

        if self._RST is not None:
            GPIO.output(self._RST, GPIO.LOW)  # Reset device
            sleep(reset_hold_time)
            GPIO.output(self._RST, GPIO.HIGH)  # Keep RESET pulled high
            sleep(reset_release_time)

    def _configure(self, pin):
        if pin is not None:
            GPIO.setup(pin, GPIO.OUT)
            return pin

    def command(self, *cmd):
        """Sends a command or sequence of commands through to the SPI device.

        :param cmd: A spread of commands.
        :type cmd: int
        """
        if self._DC:
            GPIO.output(self._DC, self._cmd_mode)

        self._write_bytes(list(cmd))

    def data(self, data):
        """Sends a data byte or sequence of data bytes through to the SPI
        device. If the data is more than :py:attr:`transfer_size` bytes, it is
        sent in chunks.

        :param data: A data sequence.
        :type data: list, bytearray
        """
        if self._DC:
            GPIO.output(self._DC, self._data_mode)

        i = 0
        n = len(data)
        tx_sz = self._transfer_size
        while i < n:
            self._write_bytes(data[i:i + tx_sz])
            i += tx_sz

    def _write_bytes(self, data):
        if self._CE:
            GPIO.output(self._CE, GPIO.LOW)  # Active low

        for byte in data:
            for _ in range(8):
                GPIO.output(self._SDA, byte & 0x80)
                GPIO.output(self._SCLK, GPIO.HIGH)
                byte <<= 1
                GPIO.output(self._SCLK, GPIO.LOW)

        if self._CE:
            GPIO.output(self._CE, GPIO.HIGH)

    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup([pin for pin in [self._SCLK, self._SDA, self._CE, self._DC, self._RST] if pin is not None])


class spi(bitbang):
    """
    Wraps an `SPI <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>`_
    (Serial Peripheral Interface) bus to provide :py:func:`data` and
    :py:func:`command` methods.

    :param port: SPI port, usually 0 (default) or 1.
    :type port: int
    :param device: SPI device, usually 0 (default) or 1.
    :type device: int
    :param bus_speed_hz: SPI bus speed, defaults to 8MHz.
    :type bus_speed_hz: int
    :param transfer_size: Maximum amount of bytes to transfer in one go. Some implementations
        only support a maximum of 64 or 128 bytes, whereas RPi/py-spidev supports
        4096 (default).
    :type transfer_size: int
    :param gpio_DC: The GPIO pin to connect data/command select (DC) to (defaults to 24).
    :type gpio_DC: int
    :param gpio_RST: The GPIO pin to connect reset (RES / RST) to (defaults to 25).
    :type gpio_RST: int
    :param spi_mode: SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], 0-3 (default:None)
    :type spi_mode: int
    :param reset_hold_time: The number of seconds to hold reset active. Some devices may require
        a duration of 100ms or more to fully reset the display (default:0)
    :type reset_hold_time: float
    :param reset_release_time: The number of seconds to delay afer reset. Some devices may require
        a duration of 150ms or more after reset was triggered before the device can accept the
        initialization sequence (default:0)
    :type reset_release_time: float
    :raises luma.core.error.DeviceNotFoundError: SPI device could not be found.
    :raises luma.core.error.UnsupportedPlatform: GPIO access not available.
    """

    def __init__(self, port=0, device=0,
                 bus_speed_hz=8000000, transfer_size=4096,
                 gpio_DC=24, gpio_RST=25, spi_mode=None,
                 reset_hold_time=0, reset_release_time=0, **kwargs):
        assert(bus_speed_hz in [mhz * 1000000 for mhz in [0.5, 1, 2, 4, 8, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50, 52]])

        bitbang.__init__(self, transfer_size, reset_hold_time, reset_release_time, DC=gpio_DC, RST=gpio_RST)

        try:
            self._spi = SpiDev()
            self._spi.open(port, device)
            if spi_mode:
                self._spi.mode = spi_mode
            if "cs_high" in kwargs:
                import warnings
                warnings.warn(
                    "SPI cs_high is no longer supported in kernel 5.4.51 and beyond, so setting parameter cs_high is now ignored!",
                    RuntimeWarning
                )
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                raise DeviceNotFoundError('SPI device not found')
            else:  # pragma: no cover
                raise

        self._spi.max_speed_hz = bus_speed_hz

    def _write_bytes(self, data):
        self._spi.writebytes(data)

    def cleanup(self):
        """Clean up SPI & GPIO resources."""
        self._spi.close()
        super(spi, self).cleanup()
