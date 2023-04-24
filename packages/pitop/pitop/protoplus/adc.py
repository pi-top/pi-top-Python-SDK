from time import sleep

from pitop.common.bitwise_ops import split_into_bytes
from pitop.common.i2c_device import I2CDevice


class ADCProbe:
    __device_address = 0x2A
    __register_address = 0
    __channel_count = 6
    __adc_ratio = 20

    def __init__(self, i2c_device_name="/dev/i2c-1"):
        self.__i2c_device_name = i2c_device_name
        self.__device = None
        self.__error_array = [-1] * self.__channel_count

    def read_value(self, channel):
        if (channel < 0) or (channel > self.__channel_count):
            print("Invalid channel - use 0 to " + str(self.__channel_count - 1))
            return -1

        results = self.read_all()

        return results[channel]

    def read_all(self):
        if self.__connect() is False:
            print("Could not connect to device")
            return self.__error_array

        results_reading = self.__device.read_n_unsigned_bytes(
            self.__register_address, number_of_bytes=self.__channel_count
        )
        results = split_into_bytes(
            results_reading, self.__channel_count, little_endian=False
        )
        data_read_len = len(results)
        self.__disconnect()

        if data_read_len != self.__channel_count:
            print(
                "Bad read from device. "
                f"Expected {str(self.__channel_count)} bytes, received {str(data_read_len)} bytes."
            )
            return self.__error_array

        for i in range(self.__channel_count):
            results[i] *= self.__adc_ratio
            results[i] = int(results[i])

        return results

    def poll(self, delay=0.5):
        print("| ADC0\t| ADC1\t| ADC2\t| ADC3\t| ADC4\t| ADC5\t|")
        print("-------------------------------------------------")

        while True:
            results = self.read_all()

            print(
                "| "
                + str(results[0])
                + "\t| "
                + str(results[1])
                + "\t| "
                + str(results[2])
                + "\t| "
                + str(results[3])
                + "\t| "
                + str(results[4])
                + "\t| "
                + str(results[5])
                + "\t|"
            )
            sleep(delay)

    def __connect(self):
        try:
            self.__device = I2CDevice(self.__i2c_device_name, self.__device_address)
            self.__device.connect()

        except Exception as e:
            print("Unable to read from ADC over I2C: " + str(e))
            return False

        return True

    def __disconnect(self):
        if self.__device is not None:
            self.__device.disconnect()
