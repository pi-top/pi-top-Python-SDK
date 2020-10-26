from ptpma import PMACamera
from time import sleep

# Record a 2s video

cam = PMACamera()

cam.start_video_capture()
sleep(2)
cam.stop_video_capture()
