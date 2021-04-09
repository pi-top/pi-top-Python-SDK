import timeit

setup_code = """
from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
from time import sleep
ball_detector = BallDetector()
from imutils import resize

camera = Camera(format="OpenCV")
sleep(2)
frame = camera.get_frame()

frame = resize(frame, width=320)

"""

main_code = """
filtered = ball_detector.colour_filter(frame, colour="red", input_format="OpenCV", output_format="OpenCV", return_binary_mask=True)
"""

print(timeit.timeit(stmt=main_code,
                    setup=setup_code,
                    number=10))




