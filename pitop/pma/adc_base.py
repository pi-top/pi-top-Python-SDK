import time
from .plate_interface import PlateInterface
from .common import get_pin_for_port


class ADCBase:
    """
    Encapsulates the behaviour of an Analog-to-Digital Converter (ADC).

    An internal class used as a base for other components.

    Contains logic to read from an Analog-to-Digital Converter. An ADC is a electronic
    component that converts an analog signal, such as a sound picked up by a microphone
    or light entering a digital camera, into a digital signal which can be processed by
    a digital circuit.

    :param str port_name: The ID for the port to which this component is connected
    """

    def __init__(self, port_name, pin_number=1):
        self._pma_port = port_name

        self.is_current = False
        self.channel = get_pin_for_port(self._pma_port, pin_number)
        self.__adc_device = PlateInterface().get_device_mcu()

    def read(self, number_of_samples=1, delay_between_samples=0.05, peak_detection=False):
        """
        Take a reading from the chosen ADC channel, or get an average value over multiple
        reads

        :param number_of_samples: Number of samples to take.
        :param delay_between_samples: Delay between taking samples (if more than one)
        :param peak_detection: Use peak detection registers (advanced)
        :return: The value read from the ADC
        :rtype: float
        """

        value = 0
        for i in range(0, number_of_samples):
            if peak_detection:
                value += self.__read_peak(self.channel)
            else:
                value += self.__read(self.channel)
            if i != number_of_samples - 1:
                time.sleep(delay_between_samples)
        return value / number_of_samples

    # input voltage / output voltage (%)
    def __read(self, channel):
        read_address = 0x30 + channel
        return self.__read_register(read_address)

    # peak detection
    def __read_peak(self, channel):
        read_address = 0x18 + channel
        return self.__read_register(read_address)

    # read 16 bits register
    def __read_register(self, read_address):
        return self.__adc_device.read_unsigned_word(read_address, little_endian=True)
