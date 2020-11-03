from .adc_base import ADCBase


class LightSensor(ADCBase):
    """
    Encapsulates the behaviour of a light sensor module.

    A simple analogue photo transistor is used to detect the intensity of the light striking
    the sensor. The component contains a photoresistor which detects light intensity. The
    resistance decreases as light intensity increases; thus the brighter the light, the
    higher the voltage.

    Uses an Analog-to-Digital Converter (ADC) to turn the analog reading from the sensor
    into a digital value.

    :param str port_name: The ID for the port to which this component is connected
    """

    @property
    def reading(self):
        """
        Take a reading from the sensor

        :return: A value representing the amount of light striking the sensor at the current time
            from 0 to 999.
        :rtype: float
        """
        return int(self.read(number_of_samples=3))

    @property
    def value(self):
        """
        Get a simple binary value based on a reading from the device

        :return: 1 if the sensor is detecting any light, 0 otherwise
        :rtype: integer
        """
        if self.reading > 0:
            return 1
        else:
            return 0
