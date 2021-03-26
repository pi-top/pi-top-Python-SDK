from pitop import Camera
from time import (
    localtime,
    sleep,
    strftime,
)

from datetime import datetime

# Example code for Camera
# Records videos of any motion captured by the camera

cam = Camera()

last_motion_detected = None


def motion_detected():
    global last_motion_detected

    last_motion_detected = datetime.now().timestamp()

    if cam.is_recording() is False:

        print("Motion detected! Starting recording...")
        output_file_name = f"/home/pi/Desktop/My Motion Recording {strftime('%Y-%m-%d %H:%M:%S', localtime(last_motion_detected))}.avi"
        cam.start_video_capture(output_file_name=output_file_name)

        while (datetime.now().timestamp() - last_motion_detected) < 3:
            sleep(1)

        cam.stop_video_capture()
        print(f"Recording completed - saved to {output_file_name}")


print("Motion detector starting...")
cam.start_detecting_motion(callback_on_motion=motion_detected, moving_object_minimum_area=350)

sleep(60)

cam.stop_detecting_motion()
print("Motion detector stopped")
