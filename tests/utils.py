from time import sleep
from typing import Callable


def wait_until(condition: Callable, timeout: int = 5) -> None:
    t = 0
    delta = 0.1
    while not condition() and t <= timeout:
        sleep(delta)
        t += delta
    if t > timeout:
        raise TimeoutError("wait_until: timeout expired")
