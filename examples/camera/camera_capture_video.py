from pitop.camera import Camera
from time import sleep

# Record a 2s video to ~/Camera/

cam = Camera()

cam.start_video_capture()
sleep(2)
cam.stop_video_capture()
