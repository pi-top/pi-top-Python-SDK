from pitop.processing import tts


class SupportsSpeech:
    def __init__(self, service_id: str = "DEFAULT"):
        self._tts = tts.services.get(service_id=service_id)

    @property
    def speak(self):
        return self._tts
