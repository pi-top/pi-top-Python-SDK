import RPi.GPIO as GPIO
from time import sleep
from time import time

min_distance_cm = 2
max_distance_cm = 400
speed_of_sound = 34300
default_trig_gpio = 23
default_echo_gpio = 27


class DistanceSensor():

    def __init__(self, trigger_gpio_pin=default_trig_gpio, echo_gpio_pin=default_echo_gpio):

        self.trigger_gpio_pin = trigger_gpio_pin
        self.echo_gpio_pin = echo_gpio_pin
        self.__setup()

    def ___setup(self):
        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_gpio_pin, GPIO.OUT)
        GPIO.setup(self.echo_gpio_pin, GPIO.IN)

    def __send_pulse(self):

        GPIO.output(self.trigger_gpio_pin, False)
        sleep(0.03)
        GPIO.output(self.trigger_gpio_pin, True)
        sleep(0.00001)
        GPIO.output(self.trigger_gpio_pin, False)

    def __get_pulse_time(self):

        timeout = time() + 0.02  # 0.02s timeout
        pulse_start = time()

        while GPIO.input(self.echo_gpio_pin) == 0:
            pulse_start = time()

            if time() > timeout:
                pulse_end = time()
                break

        while GPIO.input(self.echo_gpio_pin) == 1:
            pulse_end = time()

            if time() > timeout:
                break

        pulse_duration = pulse_end - pulse_start
        return pulse_duration

    def __get_distance_from_pulse_time(self, pulse_duration):

        pulse_duration_one_way = pulse_duration / 2
        distance = round(pulse_duration_one_way * speed_of_sound, 2)
        return distance

    def __measure_distance(self):

        self.__send_pulse()
        pulse_duration = self.__get_pulse_time()

        distance = self.__get_distance_from_pulse_time(pulse_duration)
        return distance

    @property
    def raw_distance(self):
        return self.get_raw_distance()

    @property
    def distance(self):
        return self.get_distance()

    def get_raw_distance(self):
        return self.__measure_distance()

    def get_distance(self):
        distance_set = []
        range = 100

        while range > 10:
            distance_set = []

            distance_set.append(self.__measure_distance())
            sleep(0.1)

            distance_set.append(self.__measure_distance())
            sleep(0.1)

            distance_set.append(self.__measure_distance())
            sleep(0.1)

            range = max(distance_set) - min(distance_set)

        average = sum(distance_set) / len(distance_set)
        return round(average, 2)
