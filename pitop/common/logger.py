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
        self.journal_funcs = None
        self.setup_logging(logger_name="PTLogger")

    def get_instance(self):
        """Returns the singleton instance.

        Upon its first call, it creates a new instance of the decorated
        class and calls its `__init__` method. On all subsequent calls,
        the already created instance is returned.
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError("LoggerSingleton must be accessed through `get_instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

    def __print_message(self, message, level):
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
        self.journal_funcs = {
            logging.DEBUG: self._journal_log.debug,
            logging.INFO: self._journal_log.info,
            logging.WARNING: self._journal_log.warning,
            logging.ERROR: self._journal_log.error,
        }

        if (
            systemd_journal_available is True
            and self._added_handler is False
            and log_to_journal is True
        ):
            self._journal_log.addHandler(JournalHandler())
            self._added_handler = True

        self._journal_log.setLevel(self._logging_level)
        self._journal_log.info("Logger created.")

    def __get_journal_print_func_from_log_level(self, log_level: int):
        if log_level not in self.journal_funcs:
            # Internal error
            print("Invalid log level - skipping log")
            return None

        return self.journal_funcs[log_level]

    def __log_print(self, message: str, log_level: int):
        if self._log_to_journal:
            # Journal print
            func = self.__get_journal_print_func_from_log_level(log_level)
            if func is None:
                return
            func(message)

        # stdout print
        if self._logging_level <= log_level:
            self.__print_message(message, log_level)

    def debug(self, message):
        self.__log_print(message, logging.DEBUG)

    def info(self, message):
        self.__log_print(message, logging.INFO)

    def warning(self, message):
        self.__log_print(message, logging.WARNING)

    def error(self, message):
        self.__log_print(message, logging.ERROR)


@LoggerSingleton
class PTLogger:
    def __init__(self):
        pass
