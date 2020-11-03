from os import environ
from shlex import split
from subprocess import run, Popen, CalledProcessError, TimeoutExpired

from pitop.core.logger import PTLogger
from pitop.core.current_session_info import get_first_display


def __get_env():
    env_plus_display = environ.copy()
    first_display = get_first_display()
    if first_display is not None:
        env_plus_display["DISPLAY"] = first_display
    return env_plus_display


def run_command_background(command_str: str) -> Popen:
    PTLogger.info(
        "Function: run_command_background(command_str=%s)" % command_str)
    return Popen(split(command_str), env=__get_env())


def run_command(command_str: str, timeout: int, check: bool = True, capture_output: bool = True) -> str:
    PTLogger.debug(f"Function: run_command(command_str={command_str}, timeout={timeout}, check={check}, capture_output={capture_output})")

    resp_stdout = None

    try:
        resp = run(
            split(command_str),
            check=check,
            capture_output=capture_output,
            timeout=timeout,
            env=__get_env()
        )

        if capture_output:
            resp_stdout = str(resp.stdout, 'utf8')
            resp_stderr = str(resp.stderr, 'utf8')

            PTLogger.debug(
                f"run_command(command_str='{command_str}', timeout={timeout}, check='{check}', capture_output='{capture_output}') stdout:\n{resp_stdout}")
            PTLogger.debug(
                f"run_command(command_str='{command_str}', timeout={timeout}, check='{check}', capture_output='{capture_output}') stderr:\n{resp_stderr}")

        if not check:
            PTLogger.debug(
                f"run_command(command_str='{command_str}', timeout={timeout}, check='{check}', capture_output='{capture_output}') exit code: {resp.returncode}")

    except (CalledProcessError, TimeoutExpired) as e:
        PTLogger.error(str(e))
        raise e
    except Exception as e:
        PTLogger.error(str(e))

    return resp_stdout
