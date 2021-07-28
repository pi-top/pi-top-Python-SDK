class TTS:
    __VOICES = ()

    def __init__(self):
        self._voice = None

    def __call__(self, text: str):
        print(text)

    @property
    def voice(self):
        return self._voice

    @voice.setter
    def voice(self, voice: str):
        if voice not in self.__VOICES:
            raise ValueError(f"Invalid voice choice. "
                             f"Choose from {', '.join(self.__VOICES[:-1])} or {self.__VOICES[-1]}")
        self._voice = voice

    def list_voices(self):
        print(f"Available voices: f{self.__VOICES}")
