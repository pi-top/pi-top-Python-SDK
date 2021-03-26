from pitop import Pitop
from time import sleep

pitop = Pitop()
miniscreen = pitop.miniscreen
miniscreen.display_multiline_text("Hello, world!", font_size=20)
sleep(5)
