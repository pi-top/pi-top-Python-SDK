import logging

try:
    from systemd.journal import JournalHandler

    systemd_journal_available = True
except ModuleNotFoundError:
    systemd_journal_available = False
from datetime import datetime


class LoggerSingleton:
    log_level_indicators = {10: "D", 20: "I", 30: "W", 40: "E", 50: "!"}

    def __init__(self, decorated):
        self._decorated = decorated
        self._added_handler = False
        self._instance = None
        self._logging_level = 20
        self._log_to_journal = False
        self._journal_log = None
        self.setup_logging(logger_name="PTLogger")

    def get_instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError(
            "Singletons must be accessed through `get_instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

    def _print_message(self, message, level):
        if self._log_to_journal is False and self._logging_level <= level:
            print(
                "["
                + datetime.now().strftime("%H:%M:%S.%f")
                + " "
                + self.log_level_indicators[level]
                + "] "
                + message
            )

    def setup_logging(
        self, logger_name="PTLogger", logging_level=20, log_to_journal=False
    ):
        self._logging_level = logging_level
        self._log_to_journal = log_to_journal

        self._journal_log = logging.getLogger(logger_name)

        if (
            systemd_journal_available is True
            and self._added_handler is False
            and log_to_journal is True
        ):
            self._journal_log.addHandler(JournalHandler())
            self._added_handler = True

        self._journal_log.setLevel(self._logging_level)
        self._journal_log.info("Logger created.")

    def log_print(self, message: str, log_level: int, print_method):
        self._print_message(message, log_level)
        if self._log_to_journal is True:
            print_method(message)

    def debug(self, message):
        self.log_print(message, logging.DEBUG, self._journal_log.debug)

    def info(self, message):
        self.log_print(message, logging.INFO, self._journal_log.info)

    def warning(self, message):
        self.log_print(message, logging.WARNING, self._journal_log.warning)

    def error(self, message):
        self.log_print(message, logging.ERROR, self._journal_log.error)


@LoggerSingleton
class PTLogger:
    def __init__(self):
        pass
