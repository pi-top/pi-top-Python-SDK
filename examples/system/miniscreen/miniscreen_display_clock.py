from datetime import datetime

from PIL import Image, ImageDraw
from pitop import Pitop

pitop = Pitop()
miniscreen = pitop.miniscreen
miniscreen.set_max_fps(1)

image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)
canvas = ImageDraw.Draw(image)

bounding_box = (32, 0, 95, 63)

big_hand_box = (
    bounding_box[0] + 5,
    bounding_box[1] + 5,
    bounding_box[2] - 5,
    bounding_box[3] - 5,
)

little_hand_box = (
    bounding_box[0] + 15,
    bounding_box[1] + 15,
    bounding_box[2] - 15,
    bounding_box[3] - 15,
)

while True:
    current_time = datetime.now()

    # Clear
    canvas.rectangle(bounding_box, fill=0)

    # Draw face
    canvas.ellipse(bounding_box, fill=1)

    # Draw hands
    angle_second = (current_time.second * 360 / 60) - 90
    canvas.pieslice(big_hand_box, angle_second, angle_second + 2, fill=0)

    angle_minute = (current_time.minute * 360 / 60) - 90
    canvas.pieslice(big_hand_box, angle_minute, angle_minute + 5, fill=0)

    angle_hour = (
        (current_time.hour * 360 / 12) + (current_time.minute * 360 / 12 / 60)
    ) - 90
    canvas.pieslice(little_hand_box, angle_hour, angle_hour + 5, fill=0)

    # Display to screen
    miniscreen.display_image(image)
