from argparse import ArgumentParser
from sys import exit
from pt_socket import PTSocket


def run(cli_cls):
    """Runs the CLI provided as argument, using the class properties and method.

    Args:
        cli_cls (CliBaseClass): CLI class constructor. Must inherit from CliBaseClass.
    """
    cli_name = cli_cls.cli_name
    print(f"Note: Use of the 'pt-{cli_name}' is now deprecated. Please use 'pt-config {cli_name}' instead.")

    exit_code = 1
    args = None
    ptsocket = None

    parser = ArgumentParser(prog=f'pt-{cli_name}', description=cli_cls.parser_help)
    cli_cls.add_parser_arguments(parser)
    args = parser.parse_args()

    try:    
        ptsocket = PTSocket()
        cli_object = cli_cls(ptsocket, args)
        exit_code = cli_object.run()
    except Exception as e:
        print(f"Error: {e}")
        exit_code = 1
    finally:
        if hasattr(ptsocket, "cleanup"):
            ptsocket.cleanup()
    exit(exit_code)
    
