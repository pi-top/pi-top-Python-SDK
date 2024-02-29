from .adc_base import ADCBase


class LightSensor(ADCBase):
    """Encapsulates the behaviour of a light sensor module.

    A simple analogue photo transistor is used to detect the intensity of the light striking
    the sensor. The component contains a photoresistor which detects light intensity. The
    resistance decreases as light intensity increases; thus the brighter the light, the
    higher the voltage.

    Uses an Analog-to-Digital Converter (ADC) to turn the analog reading from the sensor
    into a digital value.

    By default, the sensor uses 3 samples to report a :attr:`~.LightSensor.reading`, which takes around 0.5s.
    This can be changed by modifying the parameter :attr:`~.LightSensor.number_of_samples` in the constructor.

    :param str port_name: The ID for the port to which this component is connected
    :param str number_of_samples: Amount of sensor samples used to report a :attr:`~.LightSensor.reading`. Defaults to 3.
    :param str name: Component name, defaults to `light_sensor`. Used to access this component when added to a :class:`pitop.Pitop` object.
    """

    def __init__(
        self, port_name, pin_number=1, name="light_sensor", number_of_samples=3
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
        """Take a reading from the sensor.

        :return: A value representing the amount of light striking the
            sensor at the current time from 0 to 999.
        :rtype: float
        """
        return int(self.read())

    @property
    def value(self):
        """Get a simple binary value based on a reading from the device.

        :return: 1 if the sensor is detecting any light, 0 otherwise
        :rtype: integer
        """
        if self.reading > 0:
            return 1
        else:
            return 0

    @property
    def own_state(self):
        return {
            "value": lambda: self.value,
            "reading": lambda: self.reading,
        }
