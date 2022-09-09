import os
from io import BytesIO
from time import sleep
from typing import Callable
from PIL import Image
import pygame


def wait_until(condition: Callable, on_wait: Callable = None, timeout: int = 5) -> None:
    t = 0
    delta = 0.1
    while not condition() and t <= timeout:
        sleep(delta)
        t += delta
        if callable(on_wait):
            on_wait()
    if t > timeout:
        raise TimeoutError("wait_until: timeout expired")


def to_bytes(image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


def snapshot_simulation(simulatable):
    # save postscipt image
    pygame.image.save(simulatable._sim_screen, "temp_snapshot.png")

    # use PIL to convert to PNG bytes
    snapshot = to_bytes(Image.open("temp_snapshot.png"))

    # cleanup image
    os.remove("temp_snapshot.png")

    return snapshot
