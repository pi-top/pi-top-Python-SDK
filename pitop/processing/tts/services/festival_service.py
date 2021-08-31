import os
from .tts_service import TTSService
from threading import Thread
from typing import Optional


class FestivalBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, **kwargs):
        if self._instance is None:
            self._instance = FestivalService(**kwargs)
        return self._instance


class FestivalService(TTSService):

    __VOICE_DIR = os.path.join(os.sep, "usr", "share", "festival", "voices")

    def __init__(self, language="us", **_ignored):
        self._speed = 1.0
        self._available_voices = self.__get_available_voices()
        self._language = language
        self._voice = self._available_voices.get(self.language)[0]
        self.set_voice(self._language, self._voice)
        self._say_subprocess = None
        self._say_thread = Thread()

    def __call__(self, text: str, blocking: bool = True):
        self.say(text=text, blocking=blocking)

    def say(self, text: str, blocking: bool = True) -> None:
        if not self.__validate_request(text):
            return

        self._say_thread = Thread(target=self.__festival_say_commands, args=(text,), daemon=True)
        self._say_thread.start()

        if blocking:
            self._say_thread.join()

    def __festival_say_commands(self, text):
        # Have to import festival within the thread since it doesn't work with multi-threading
        # As a result, have to set voice and stretch factor with every call
        import festival
        festival.execCommand(f"(voice_{self.voice})")
        festival.setStretchFactor(1 / self.speed)
        festival.sayText(text)

    def __validate_request(self, text):
        if text == "" or type(text) != str:
            raise ValueError("Text must be a string and cannot be empty.")

        if self._say_thread.is_alive():
            print("Speech already in progress, request cancelled.")
            return False

        return True

    def __get_available_voices(self):
        languages = os.listdir(self.__VOICE_DIR)
        language_dirs = (os.path.join(self.__VOICE_DIR, lang) for lang in languages)

        voice_dict = {}
        for lang, lang_dir in zip(languages, language_dirs):
            voice_dict[lang] = os.listdir(lang_dir)

        return voice_dict

    @property
    def available_voices(self) -> dict:
        return self._available_voices

    def set_voice(self, language: str, voice: Optional[str] = None) -> None:
        available_languages = list(self._available_voices.keys())
        if language not in available_languages:
            raise ValueError("Invalid language choice. Please choose from:\n"
                             f"{available_languages}")

        available_voices = self._available_voices.get(language)

        voice = available_voices[0] if voice is None else voice

        if voice not in available_voices:
            raise ValueError(f"Invalid voice choice. Please choose from:\n"
                             f"{available_voices}\n"
                             f"Or choose a different language. "
                             f"Run display_voices() method to see what is available.")

        self._voice = voice
        self._language = language

    @property
    def voice(self):
        return self._voice

    @property
    def language(self):
        return self._language

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: float):
        if value < 0.2:
            raise ValueError("Speed value must be greater than or equal to 0.2.")

        self._speed = value
