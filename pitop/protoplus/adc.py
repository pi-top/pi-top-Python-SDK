from pitopcommon.i2c_device import I2CDevice
from time import sleep


class ADCProbe():

    _device_address = 0x2A
    _channel_count = 6
    _adc_ratio = 20

    def __init__(self, i2c_device_name="/dev/i2c-1"):

        self._i2c_device_name = i2c_device_name
        self._device = None
        self._error_array = [-1] * self._channel_count

    def read_value(self, channel):

        if ((channel < 0) or (channel > self._channel_count)):
            print("Invalid channel - use 0 to " + str(self._channel_count - 1))
            return -1

        results = self.read_all()

        return results[channel]

    def read_all(self):

        if (self._connect() is False):
            print("Could not connect to device")
            return self._error_array

        results = self._device._read_data(self._channel_count)
        data_read_len = len(results)
        self._disconnect()

        if (data_read_len != self._channel_count):
            print("Bad read from device. Expected " +
                  str(self._channel_count) + " bytes, received: " + data_read_len)
            return self._error_array

        for i in range(self._channel_count):
            results[i] *= self._adc_ratio
            results[i] = int(results[i])

        return results

    def poll(self, delay=0.5):

        print("| ADC0\t| ADC1\t| ADC2\t| ADC3\t| ADC4\t| ADC5\t|")
        print("-------------------------------------------------")

        while True:

            results = self.read_all()

            print("| " + str(results[0]) + "\t| " + str(results[1]) + "\t| " + str(results[2]) +
                  "\t| " + str(results[3]) + "\t| " + str(results[4]) + "\t| " + str(results[5]) + "\t|")
            sleep(delay)

    def _connect(self):

        try:
            self._device = I2CDevice(
                self._i2c_device_name, self._device_address)
            self._device.connect()

        except Exception as e:
            print("Unable to read from ADC over I2C: " + str(e))
            return False

        return True

    def _disconnect(self):

        if (self._device is not None):
            self._device.disconnect()
