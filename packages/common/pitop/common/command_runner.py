import logging
from os import environ
from shlex import split
from subprocess import DEVNULL, CalledProcessError, Popen, TimeoutExpired, run

from pitop.common.current_session_info import get_first_display

logger = logging.getLogger(__name__)


def __get_env():
    env = environ.copy()
    first_display = get_first_display()
    if first_display is not None:
        env["DISPLAY"] = first_display

    # Print output of commands in english
    env["LANG"] = "en_US.UTF-8"

    return env


def run_command_background(command_str: str, print_output=False) -> Popen:
    logger.debug("Function: run_command_background(command_str=%s)" % command_str)

    return Popen(
        split(command_str),
        env=__get_env(),
        stderr=None if print_output else DEVNULL,
        stdout=None if print_output else DEVNULL,
    )


def run_command(
    command_str: str,
    timeout: int,
    check: bool = True,
    capture_output: bool = True,
    log_errors: bool = True,
    lower_priority: bool = False,
) -> str:
    logger.debug(
        f"Function: run_command(command_str={command_str}, timeout={timeout}, check={check}, capture_output={capture_output}, \
         log_errors={log_errors}, lower_priority={lower_priority})"
    )

    resp_stdout = None

    if lower_priority:
        command_str = "nice -n 10 " + command_str

    try:
        resp = run(
            split(command_str),
            check=check,
            capture_output=capture_output,
            timeout=timeout,
            env=__get_env(),
        )

    except (CalledProcessError, TimeoutExpired) as e:
        if log_errors:
            logger.error(str(e))
        raise e
    except Exception as e:
        if log_errors:
            logger.error(str(e))
        return ""

    if capture_output:
        resp_stdout = str(resp.stdout, "utf8")
        resp_stderr = str(resp.stderr, "utf8")

        logger.debug(
            f"run_command("
            f"command_str='{command_str}', "
            f"timeout={timeout}, "
            f"check='{check}', "
            f"capture_output='{capture_output}'"
            f") stdout:\n{resp_stdout}"
        )
        logger.debug(
            f"run_command("
            f"command_str='{command_str}', "
            f"timeout={timeout}, "
            f"check='{check}', "
            f"capture_output='{capture_output}'"
            f") stderr:\n{resp_stderr}"
        )

    if not check:
        logger.debug(
            f"run_command("
            f"command_str='{command_str}', "
            f"timeout={timeout}, "
            f"check='{check}', "
            f"capture_output='{capture_output}'"
            f") exit code: {resp.returncode}"
        )

    return resp_stdout
