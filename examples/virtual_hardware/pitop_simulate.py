from pitop.virtual_hardware import simulate, use_virtual_hardware

use_virtual_hardware()

from time import sleep

from pitop import Pitop
from pitop.pma import LED, Button

pitop = Pitop()
pitop.add_component(LED("D0", name="led1"))
pitop.add_component(Button("D1", name="button1"))
pitop.add_component(LED("D2", name="led2", color="green"))
pitop.add_component(Button("D3", name="button2"))
pitop.add_component(LED("D4", name="led3"))
pitop.add_component(Button("D5", name="button3"))
pitop.add_component(LED("D6", name="led4", color="yellow"))
pitop.add_component(Button("D7", name="button4"))

pitop.button1.when_pressed = pitop.led1.on
pitop.button1.when_released = pitop.led1.off

pitop.button2.when_pressed = pitop.led2.on
pitop.button2.when_released = pitop.led2.off

pitop.button3.when_pressed = pitop.led3.on
pitop.button3.when_released = pitop.led3.off

pitop.button4.when_pressed = pitop.led4.on
pitop.button4.when_released = pitop.led4.off

pitop_sim = simulate(pitop)
led_sim = simulate(pitop.led4)
button_sim = simulate(pitop.button4)

import pygame

#for i in range(30):
#    pitop.miniscreen.display_text(i)
#    pitop_sim.event(pygame.MOUSEBUTTONDOWN, "button4")
#    sleep(1)
#    pitop_sim.event(pygame.MOUSEBUTTONUP, "button4")
#    sleep(1)

from urllib.request import urlopen
from PIL import Image
from requests.models import PreparedRequest
from urllib.parse import urlencode
import json

from random import randint
from signal import pause

SEARCH_LIMIT = 10
SEARCH_TERM = "Monochrome"
API_KEY = "tBqjj75LwgYGIyrtvInrxOnHo6BcHTaI"
req = PreparedRequest()
req.prepare_url(
    "http://api.giphy.com/v1/gifs/search",
    urlencode({"q": SEARCH_TERM, "api_key": API_KEY, "limit": f"{SEARCH_LIMIT}"}),
)
def play_random_gif():
    global gif

    # Show "Loading..." while processing for a GIF
    pitop.miniscreen.display_multiline_text("Loading random GIF...", font_size=18)


    print('loading')
    # Get GIF data from Giphy
    with urlopen(req.url) as response:
        data = json.loads(response.read())

    print('processing')
    # Extract random GIF URL from JSON response
    gif_url = data["data"][randint(0, SEARCH_LIMIT - 1)]["images"]["fixed_height"][
        "url"
    ]
    print('opening')

    # Load GIF from URL
    gif = Image.open(urlopen(gif_url))

    print('go')
    # Play one loop of GIF animation
    pitop.miniscreen.play_animated_image(gif)
    pitop.miniscreen.play_animated_image(gif)
    pitop.miniscreen.play_animated_image(gif)

while True:
    play_random_gif()

pitop_sim.stop()
led_sim.stop()
button_sim.stop()
