from configparser import ConfigParser
from os import environ
from pathlib import Path
from threading import Lock
from typing import Dict, Set


class StateManager:
    _instances: Dict[str, "StateManager"] = {}
    _initialized: Set[str] = set()

    def __new__(cls, name: str):
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, name: str):
        # Skip initialization if already done for this package
        if name in StateManager._initialized:
            return

        self.name = name

        # Initialize state file
        path = Path(self.path)
        if not path.exists():
            Path(path.parent).mkdir(parents=True, exist_ok=True)
            path.touch()

        self.config_parser = ConfigParser()
        self.config_parser.read(self.path)

        self.lock = Lock()
        StateManager._initialized.add(name)

    @staticmethod
    def exists(name: str) -> bool:
        return Path(StateManager.get_file_path(name)).exists()

    @staticmethod
    def folder(name: str) -> str:
        testing = environ.get("TESTING", "") == "1"
        base = "/tmp" if testing else "/var/lib"
        return f"{base}/{name}"

    @staticmethod
    def get_file_path(name: str) -> str:
        return f"{StateManager.folder(name)}/state.cfg"

    @property
    def path(self) -> str:
        return StateManager.get_file_path(self.name)

    def _cleanup(self):
        if hasattr(self, "name"):
            StateManager._initialized.discard(self.name)
            StateManager._instances.pop(self.name, None)

    def __del__(self):
        self._cleanup()

    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup()

    def get(self, section: str, key: str, fallback=None):
        with self.lock:
            val = fallback
            try:
                val = self.config_parser.get(section, key)
            except Exception:
                if fallback is None:
                    raise
            return val

    def set(self, section: str, key: str, value):
        for data_to_validate in [section, key]:
            if not isinstance(data_to_validate, str) or len(data_to_validate) == 0:
                raise ValueError("Section and key must be non-empty strings")

        with self.lock:
            try:
                if not self.config_parser.has_section(section):
                    self.config_parser.add_section(section)
                self.config_parser.set(section, key, value)
            except Exception:
                raise
            self._save()

    def remove_section(self, section: str):
        if section not in self.config_parser.sections():
            return
        with self.lock:
            self.config_parser.remove_section(section)
            self._save()

    def remove_key(self, section: str, key: str):
        if section not in self.config_parser.sections():
            return
        if key not in self.config_parser[section]:
            return
        with self.lock:
            self.config_parser.remove_option(section, key)
            self._save()

    def _save(self):
        with open(self.path, "w") as f:
            self.config_parser.write(f)
