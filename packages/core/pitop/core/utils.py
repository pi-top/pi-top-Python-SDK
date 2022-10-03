from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull


@contextmanager
def suppress_output():
    """Redirects stdout and stderr to devnull."""
    with open(devnull, "w") as null:
        with redirect_stderr(null) as err, redirect_stdout(null) as out:
            yield (err, out)
