from time import sleep

import cv2
from pitop import Camera, Pitop

miniscreen = Pitop().miniscreen

cam = Camera(format="OpenCV", flip_top_bottom=True)
directory = "images/"
button = miniscreen.select_button
picture_count = 0


while True:
    frame = cam.get_frame()

    cv2.imshow("Frame", frame)
    miniscreen.display_image(frame)
    if button.is_pressed:
        cv2.imwrite(f"{directory}image_{picture_count}.jpg", frame)
        print(f"Frame written to file with ID: {picture_count}\n")
        picture_count += 1
        sleep(0.5)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cv2.destroyAllWindows()
