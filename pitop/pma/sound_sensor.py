from .adc_base import ADCBase


class SoundSensor(ADCBase):
    """
    Encapsulates the behaviour of a sound sensor.

    A sound sensor component is typically a simple microphone that detects the vibrations
    of the air entering the sensor and produces an analog reading based on the amplitude
    of these vibrations.

    Uses an Analog-to-Digital Converter (ADC) to turn the analog reading from the sensor
    into a digital value.

    :param str port_name: The ID for the port to which this component is connected
    """

    @property
    def reading(self):
        """
        Take a reading from the sensor

        :return: A value representing the volume of sound detected by the sensor at the current time
        :rtype: float
        """
        reading = self.read(peak_detection=True) / 2
        return reading

    @property
    def value(self):
        """
        Get a simple binary value based on a reading from the device

        :return: 1 if the sensor is detecting any sound, 0 otherwise
        :rtype: integer
        """
        value = self.reading
        return 0 if value == 0 else 1
