from .adc_base import ADCBase


class Potentiometer(ADCBase):
    """Encapsulates the behaviour of a potentiometer.

    A potentiometer is a three-terminal resistor with a sliding or rotating contact that forms an
    adjustable voltage divider. The component is used for measuring the electric potential (voltage)
    between the two 'end' terminals. If only two of the terminals are used, one end and the wiper,
    it acts as a variable resistor or rheostat. Potentiometers are commonly used to control
    electrical devices such as volume controls on audio equipment.

    Uses an Analog-to-Digital Converter (ADC) to turn the analog reading from the sensor
    into a digital value.

    :param str port_name: The ID for the port to which this component is connected
    :param str number_of_samples: Amount of sensor samples used to report a :attr:`~.Potentiometer.position`. Defaults to 1.
    :param str name: Component name, defaults to `potentiometer`. Used to access this component when added to a :class:`pitop.Pitop` object.
    """

    def __init__(
        self, port_name, pin_number=1, name="potentiometer", number_of_samples=1
    ):
        ADCBase.__init__(
            self,
            port_name=port_name,
            pin_number=pin_number,
            name=name,
            number_of_samples=number_of_samples,
        )

    @property
    def own_state(self):
        return {
            "position": lambda: self.position,
        }

    @property
    def position(self):
        """Get the current reading from the sensor.

        :return: A value representing the potential difference (voltage)
            from 0 to 999.
        :rtype: float
        """
        return self.read()

    @property
    def value(self):
        """Get a simple binary value based on a reading from the device.

        :return: 1 if the sensor is detecting a potential difference
            (voltage), 0 otherwise
        :rtype: integer
        """
        if self.position > 0:
            return 1
        else:
            return 0
