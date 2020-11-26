from argparse import ArgumentParser
from sys import exit, stderr

# This file serves as support for deprecated CLI paths, that will be removed in the future.


def run(cli_cls):
    """Runs the CLI provided as argument, using the class properties and method.

    Args:
        cli_cls (CliBaseClass): CLI class constructor. Must inherit from CliBaseClass.
    """
    cli_name = cli_cls.cli_name
    print(
        f"Note: Use of the 'pt-{cli_name}' is now deprecated. "
        f"Please use 'pi-top {cli_name}' instead.", file=stderr)

    exit_code = 1
    args = None

    parser = ArgumentParser(prog=f'pt-{cli_name}', description=cli_cls.parser_help)
    cli_cls.add_parser_arguments(parser)
    args = parser.parse_args()

    try:
        cli_object = cli_cls(args)
        exit_code = cli_object.run()

    except Exception as e:
        print(f"Error: {e}")
        exit_code = 1

    exit(exit_code)
