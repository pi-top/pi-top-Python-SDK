from pitop import Pitop, Camera
from time import sleep
from os import environ
from pitopcommon.current_session_info import get_first_display
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()

environ["DISPLAY"] = get_first_display()

miniscreen = Pitop().miniscreen

cam = Camera(format="OpenCV", flip_top_bottom=True)
directory = "images/"
button = miniscreen.select_button

picture_count = 0


while True:
    frame = cam.get_frame()

    cv2.imshow("Frame", frame)
    if button.is_pressed:
        cv2.imwrite(f'{directory}image_{picture_count}.jpg', frame)
        print(f"Frame written to file with ID: {picture_count}\n")
        picture_count += 1
        sleep(0.5)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
