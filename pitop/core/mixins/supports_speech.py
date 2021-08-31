from pitop.processing import tts
from pitop.processing.tts.services.tts_service import TTSService


class SupportsSpeech:
    def __init__(self, service_id: str = "DEFAULT"):
        self._tts = tts.services.get(service_id=service_id)

    @property
    def speak(self):
        return self._tts

    @speak.setter
    def speak(self, service: TTSService):
        self._tts = service

    @classmethod
    def using_speech_service(cls, service_id):
        obj = cls()
        speech_service = tts.services.get(service_id=service_id)
        obj.speak = speech_service
        return obj
