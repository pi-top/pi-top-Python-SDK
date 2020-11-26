from argparse import ArgumentParser
from sys import exit, stderr
from pitopcommon.ptdm_request_client import PTDMRequestClient


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
    request_client = None

    parser = ArgumentParser(prog=f'pt-{cli_name}', description=cli_cls.parser_help)
    cli_cls.add_parser_arguments(parser)
    args = parser.parse_args()

    try:
        request_client = PTDMRequestClient()
        cli_object = cli_cls(request_client, args)
        exit_code = cli_object.run()
    except Exception as e:
        print(f"Error: {e}")
        exit_code = 1
    finally:
        if hasattr(request_client, "cleanup"):
            request_client.cleanup()
    exit(exit_code)
