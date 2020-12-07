from argparse import ArgumentParser
from sys import exit, stderr

# This file serves as support for deprecated CLI paths, that will be removed in the future.


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def __run(cli_cls, args):
    exit_code = 1
    try:
        cli_object = cli_cls(args)
        exit_code = cli_object.run()
    except Exception as e:
        print(f"Error: {e}")
        exit_code = 1
    exit(exit_code)


def run(cli_cls):
    """Runs the CLI provided as argument, using the class properties and methods.

    Args:
        cli_cls (CliBaseClass): CLI class constructor. Must inherit from CliBaseClass.
    """
    cli_name = cli_cls.cli_name
    print(
        f"Note: Use of 'pt-{cli_name}' is now deprecated. "
        f"Please use 'pi-top {cli_name}' instead.", file=stderr)

    parser = ArgumentParser(prog=f'pt-{cli_name}', description=cli_cls.parser_help)
    cli_cls.add_parser_arguments(parser)
    args = parser.parse_args()
    __run(cli_cls, args)


def run_with_args(cli_cls, old_command, new_command, args_dict):
    """Runs a CLI command using the provided 'cli_cls' and the arguments in 'args_dict'.
    This method doesn't use ArgumentParser, since it directly executes
    the CLI command using static arguments provided in 'args_dict'.

    Args:
        cli_cls (CliBaseClass): CLI class constructor. Must inherit from CliBaseClass.
        old_command (str): string with the deprecated CLI command
        new_command (str): string with the new CLI command
        args_dict (dict): dictionary with the arguments and values assigned to run the CLI
    """
    print(
        f"Note: Use of '{old_command}' is now deprecated. "
        f"Please use '{new_command}' instead.", file=stderr)
    __run(cli_cls, dotdict(args_dict))
