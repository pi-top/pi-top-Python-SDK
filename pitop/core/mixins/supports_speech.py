class SupportsSpeech:
    def __init__(self):
        from pitop.processing.speech import services
        self._tts = services.get("DEFAULT")

    @property
    def speak(self):
        return self._tts
