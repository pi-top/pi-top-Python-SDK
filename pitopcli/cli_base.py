from abc import ABC, abstractmethod, abstractproperty


class PitopCliException(Exception):
    pass


class PitopCliInvalidArgument(Exception):
    pass


class CliBaseClass(ABC):
    """Abstract class, used to create CLI commands"""
    @abstractmethod
    def __init__(self, args):
        """Class constructor.

        Args:
            args (Namespace): arguments as returned by Argparse.parse_args
        """
        pass

    @abstractmethod
    def run(self):
        """Executes the action performed by the CLI"""
        pass

    @classmethod
    @abstractmethod
    def add_parser_arguments(cls, parser):
        """Add CLI expected arguments to the provided parser

        Args:
            parser (argparse._SubParsersAction | argparse.ArgumentParser): parser where class arguments will be appended
        """
        pass

    @property
    @abstractproperty
    def parser_help(self):
        """Help string to be displayed by ArgumentParser"""
        pass

    @property
    @abstractproperty
    def cli_name(self):
        """Name of the class CLI, without the 'pt-' prefix"""
        pass

    @property
    def parser(self):
        """ArgumentParser object used to parse the class"""
        pass

    def validate_args(self):
        """Method to perform further validation on arguments"""
        pass
