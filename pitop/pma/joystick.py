from .adc_base import ADCBase


class Joystick:
    '''
    Thumb Joystick class
    '''

    def __init__(self, port_name):
        self._adc_x = ADCBase(port_name=port_name, pin_number=1)
        self._adc_y = ADCBase(port_name=port_name, pin_number=2)

    @property
    def value(self):
        '''
        :returns float value: tuple (x, y)
        '''
        return self._adc_x.read(), self._adc_y.read()
