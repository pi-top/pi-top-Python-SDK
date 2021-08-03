import json
from configparser import ConfigParser
from os import geteuid
from random import randint
from signal import pause
from sys import exit
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen

from PIL import Image
from pitop.miniscreen import Miniscreen
from requests.models import PreparedRequest


def is_root():
    return geteuid() == 0


if not is_root():
    print("Admin access required - please run this script with 'sudo'.")
    exit()

# Define Giphy parameters
SEARCH_LIMIT = 10
SEARCH_TERM = "Monochrome"

CONFIG_FILE_PATH = "/etc/pt-miniscreen/settings.ini"
STARTUP_GIF_PATH = "/home/pi/miniscreen-startup.gif"


API_KEY = "<MY GIPHY KEY>"

# Define global variables
gif = None
miniscreen = Miniscreen()
req = PreparedRequest()
req.prepare_url(
    "http://api.giphy.com/v1/gifs/search",
    urlencode({"q": SEARCH_TERM, "api_key": API_KEY, "limit": f"{SEARCH_LIMIT}"}),
)


def display_instructions_dialog():
    miniscreen.select_button.when_pressed = play_random_gif
    miniscreen.cancel_button.when_pressed = None
    miniscreen.display_multiline_text(
        "Press SELECT to load a random GIF!", font_size=18
    )


def display_user_action_select_dialog():
    miniscreen.select_button.when_pressed = save_gif_as_startup
    miniscreen.cancel_button.when_pressed = play_random_gif
    miniscreen.display_multiline_text(
        "SELECT: save GIF as default startup animation. CANCEL: load new GIF",
        font_size=12,
    )


def display_loading_dialog():
    miniscreen.select_button.when_pressed = None
    miniscreen.cancel_button.when_pressed = display_instructions_dialog
    miniscreen.display_multiline_text("Loading random GIF...", font_size=18)


def display_saving_dialog():
    miniscreen.select_button.when_pressed = None
    miniscreen.cancel_button.when_pressed = None
    miniscreen.display_multiline_text(
        "GIF saved as default startup animation!", font_size=18
    )
    # Saving is fast, so we need to wait a short while for the message to be seen on the display
    sleep(1)


def play_random_gif():
    global gif

    # Show "Loading..." while processing for a GIF
    display_loading_dialog()

    # Get GIF data from Giphy
    with urlopen(req.url) as response:
        data = json.loads(response.read())

    # Extract random GIF URL from JSON response
    gif_url = data["data"][randint(0, SEARCH_LIMIT - 1)]["images"]["fixed_height"][
        "url"
    ]

    # Load GIF from URL
    gif = Image.open(urlopen(gif_url))

    # Play one loop of GIF animation
    miniscreen.play_animated_image(gif)

    # Ask user if they want to save it
    display_user_action_select_dialog()


def save_gif_as_startup():
    # Display "saving" dialog
    display_saving_dialog()

    # Save file to home directory
    gif.save(STARTUP_GIF_PATH, save_all=True)

    config = ConfigParser()
    cfg_section = "Bootsplash"

    if not config.has_section(cfg_section):
        config.add_section(cfg_section)

    config.set(cfg_section, "Path", STARTUP_GIF_PATH)

    with open(CONFIG_FILE_PATH, "w") as f:
        config.write(f)

    # Go back to the start
    display_instructions_dialog()


# Display initial dialog
display_instructions_dialog()

# Wait indefinitely for user input
pause()
