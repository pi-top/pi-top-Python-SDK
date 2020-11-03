from pitop.pma import Camera
from time import sleep

# Record a 2s video

cam = Camera()

cam.start_video_capture()
sleep(2)
cam.stop_video_capture()
