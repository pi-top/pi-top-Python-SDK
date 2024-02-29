from pitop.pma.adc_base import ADCBase


class SoundSensor(ADCBase):
    """Encapsulates the behaviour of a sound sensor.

    A sound sensor component is typically a simple microphone that detects the vibrations
    of the air entering the sensor and produces an analog reading based on the amplitude
    of these vibrations.

    Uses an Analog-to-Digital Converter (ADC) to turn the analog reading from the sensor
    into a digital value.

    :param str port_name: The ID for the port to which this component is connected
    :param str number_of_samples: Amount of sensor samples used to report a :attr:`~.SoundSensor.reading`. Defaults to 1.
    :param str name: Component name, defaults to `sound_sensor`. Used to access this component when added to a :class:`pitop.Pitop` object.
    """

    def __init__(
        self, port_name, pin_number=1, name="sound_sensor", number_of_samples=1
    ):
        ADCBase.__init__(
            self,
            port_name=port_name,
            pin_number=pin_number,
            name=name,
            number_of_samples=number_of_samples,
        )

    @property
    def reading(self):
        """Take a reading from the sensor. Uses a builtin peak detection system
        to retrieve the sound level.

        :return: A value representing the volume of sound detected by
            the sensor at the current time from 0 to 500.
        :rtype: float
        """
        return self.read(peak_detection=True) / 2

    @property
    def value(self):
        """Get a simple binary value based on a reading from the device.

        :return: 1 if the sensor is detecting any sound, 0 otherwise
        :rtype: integer
        """
        value = self.reading
        return 0 if value == 0 else 1

    @property
    def own_state(self):
        return {
            "value": lambda: self.value,
            "reading": lambda: self.reading,
        }
