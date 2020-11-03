from pitop.pma import Camera
from time import sleep
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
        cam.start_video_capture()

        while (datetime.now().timestamp() - last_motion_detected) < 3:
            sleep(1)

        cam.stop_video_capture()
        print("Recording completed")

    else:
        print("Further motion detected. Continue recording...")


print("Motion detector starting...")
cam.start_detecting_motion(motion_detected, 350)

sleep(60)

cam.stop_detecting_motion()
print("Motion detector stopped")
