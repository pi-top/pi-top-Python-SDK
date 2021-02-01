from pitop.camera import Camera
from time import sleep

# Record a 10s video to ~/Camera/

cam = Camera()

cam.start_video_capture()
sleep(10)
cam.stop_video_capture()
