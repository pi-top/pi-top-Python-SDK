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


# TkInter widgets are not renderable using Postscript so we must use regular
# images to render them for our snapshots
def create_widget_mock(Widget):
    class MockWidget(Widget):
        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            self.__render_image(kwargs.get("image", None))

        def place(self, *args, **kwargs):
            super().place(*args, **kwargs)

            if hasattr(self, "_mock_image"):
                self.__render_image(self._mock_image)

        def __render_image(self, image=None):
            if image is None:
                return

            # make sure the position is correct
            self.master.update()

            # clear old mock image
            if hasattr(self, "_mock_image_sprite_id"):
                self.master.itemconfigure(self._mock_image_sprite_id, image="")

            # create new mock image positioned in the same place as the button
            self._mock_image = image
            self._mock_image_sprite_id = self.master.create_image(
                self.winfo_x() + int(self.winfo_width() / 2),
                self.winfo_y() + int(self.winfo_height() / 2),
            )
            self.master.itemconfigure(self._mock_image_sprite_id, image=image)

    return MockWidget
