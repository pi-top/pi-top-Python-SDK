# Example code to draw an analog clock

from pitop.miniscreen import OLED
from datetime import datetime

oled = OLED()
oled.set_max_fps(1)
canvas = oled.canvas

clock_face_box = canvas.get_bounding_box()
big_hand_box = (clock_face_box[0] + 5,
                clock_face_box[1] + 5,
                clock_face_box[2] - 5,
                clock_face_box[3] - 5)
little_hand_box = (clock_face_box[0] + 15,
                   clock_face_box[1] + 15,
                   clock_face_box[2] - 15,
                   clock_face_box[3] - 15)

while True:
    current_time = datetime.now()

    canvas.clear()
    canvas.ellipse(clock_face_box, 1, 1)

    angle_second = (current_time.second * 360 / 60) - 90
    canvas.pieslice(big_hand_box, angle_second, angle_second + 2, 0, 0)

    angle_minute = (current_time.minute * 360 / 60) - 90
    canvas.pieslice(big_hand_box, angle_minute, angle_minute + 5, 0, 0)

    angle_hour = ((current_time.hour * 360 / 12) +
                  (current_time.minute * 360 / 12 / 60)) - 90
    canvas.pieslice(little_hand_box, angle_hour, angle_hour + 5, 0, 0)

    oled.draw()
