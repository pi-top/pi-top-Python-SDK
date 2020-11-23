import pyaudio
from os import system
from math import pi
from math import sin
from time import sleep
from struct import pack
from threading import Thread

# Make sure that PulseAudio is running
system("pulseaudio --start --high-priority=yes --realtime=yes")
sleep(1)


class beep:
    FRAME_RATE = 22050
    _TWO_PI = 2 * pi
    frequency = 750
    volume = 1    # range [0.0, 1.0]

    def __init__(self):
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(format=self._p.get_format_from_width(2),
                                    channels=1,
                                    rate=self.FRAME_RATE,
                                    output=True)

    def __del__(self):
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()

    def _frequency_generator(self):
        while True:
            yield self.frequency

    def _variable_tone(self, frequency):
        time_scale = self._TWO_PI / self.FRAME_RATE
        phase = 0
        data = b''
        for f in frequency:
            if len(data) > 256:
                yield data
                data = b''
            raw_val = (self.volume * sin(phase))
            if raw_val > 1:
                raw_val = 1
            elif raw_val < -1:
                raw_val = -1
            data += pack('<h', int(raw_val * 32687))
            phase += time_scale * f
            # don't reset hard to zero – avoids sudden phase glitches due to rounding error
            if phase > self._TWO_PI:
                phase -= self._TWO_PI

    def _play(self):
        for i in self._variable_tone(self._frequency_generator()):
            self._stream.write(i)

    def play(self):
        Thread(target=self._play).start()
