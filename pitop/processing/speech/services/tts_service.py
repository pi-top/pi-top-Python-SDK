from abc import (
    ABCMeta,
    abstractmethod,
)


class AttributeMeta(ABCMeta):
    """Metaclass for ensuring children of abstract base class define specified
    attributes."""
    required_attributes = []

    def __call__(cls, *args, **kwargs):
        obj = super(AttributeMeta, cls).__call__(*args, **kwargs)
        for attr_name in obj.required_attributes:
            if not getattr(obj, attr_name):
                raise ValueError('required attribute (%s) not set' % attr_name)
        return obj


class TTSService(metaclass=AttributeMeta):
    required_attributes = ['_voice', '_available_voices', '_language', '_speed']

    @abstractmethod
    def __call__(self, text: str, blocking: bool = True) -> None:
        pass

    @abstractmethod
    def say(self, text: str, blocking: bool = True) -> None:
        pass

    @property
    @abstractmethod
    def available_voices(self) -> dict:
        pass

    @abstractmethod
    def set_voice(self, language: str, name: str) -> None:
        pass

    @property
    @abstractmethod
    def voice(self) -> str:
        pass

    @property
    @abstractmethod
    def language(self) -> str:
        pass

    @property
    @abstractmethod
    def speed(self):
        pass

    @speed.setter
    @abstractmethod
    def speed(self, speed: float):
        pass

    def print_voices(self):
        print("LANGUAGE   VOICES")
        print("--------   ------")
        for language, voices in self.available_voices.items():
            print(f"{language:<10} {', '.join(voices)}")
        print()
