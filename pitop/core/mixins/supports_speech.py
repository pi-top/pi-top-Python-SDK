from pitop.core.exceptions import UnavailableComponent
from pitop.system import device_type

from pitopcommon.common_names import DeviceName


class SupportsSpeech:
    def __init__(self):
        from pitop.processing.speech import TTS
        self._tts = None
        if device_type() == DeviceName.pi_top_4.value:
            # TODO: probably unnecessary, can work on any device with a speaker
            self._tts = TTS()

    @property
    def speak(self):
        if self._tts:
            return self._tts
        raise UnavailableComponent("Speech isn't available on this device")
