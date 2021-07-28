class SupportsSpeech:
    def __init__(self):
        from pitop.processing.speech import TTS
        self._tts = TTS()

    @property
    def speak(self):
        return self._tts
