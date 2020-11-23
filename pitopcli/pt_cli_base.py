from abc import ABC, abstractmethod, abstractproperty


class CliBaseClass(ABC):
    """Abstract class, used to create CLI commands"""
    @abstractmethod
    def __init__(self, pt_socket, args):
        """Class constructor.

        Args:
            pt_socket (pt_socket.PTSocket): socket used to communicate with pt-device-manager
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
