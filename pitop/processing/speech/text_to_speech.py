import festival
import os


class TTS:
    __VOICE_DIR = os.path.join(os.sep, "usr", "share", "festival", "voices")

    def __init__(self):
        self._speed = 1.0
        self.__voices = self.get_voices()
        self._language = None
        self.language = "us"
        self._voice = None
        self.voice = self.__voices.get(self.language)[0]

    def __call__(self, text: str):
        festival.sayText(text)

    def get_voices(self):
        languages = os.listdir(self.__VOICE_DIR)
        language_dirs = (os.path.join(self.__VOICE_DIR, lang) for lang in languages)

        voice_dict = {}
        for lang, lang_dir in zip(languages, language_dirs):
            voice_dict[lang] = os.listdir(lang_dir)

        return voice_dict

    @property
    def voice(self):
        return self._voice

    @voice.setter
    def voice(self, voice: str):
        available_voices = self.__voices.get(self.language)
        if voice not in available_voices:
            raise ValueError(f"Invalid voice choice. Please choose from:\n"
                             f"{available_voices}\n"
                             f"Or choose a different language. Run display_voices() method to see what is available.")
        self._voice = voice
        success = festival.execCommand(f"(voice_{self._voice})")
        if not success:
            print("Changing voice failed.")

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, language: str):
        available_languages = list(self.__voices.keys())
        if language not in available_languages:
            raise ValueError("Invalid language choice. Please choose from:\n"
                             f"{available_languages}")
        self._language = language

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: float):
        if value < 0.2:
            raise ValueError("Speed value must be greater than or equal to 0.2.")

        self._speed = value
        success = festival.setStretchFactor(1 / self._speed)

        if not success:
            print("Changing speed failed.")

    def display_voices(self):
        print("LANGUAGE   VOICES")
        for language, voices in self.__voices.items():
            print(f"{language:<10} {', '.join(voices)}")
        print()
