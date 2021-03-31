import cv2
from os import environ
from signal import pause

from pitopcommon.current_session_info import get_first_display
from pitop import Camera
from pitop.processing.algorithms.faces import FaceDetector


environ["DISPLAY"] = get_first_display()


def find_faces(frame):
    face = face_detector.detect(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        print(f"Face angle: {face.angle} \n"
              f"Face center: {face.center} \n"
              f"Face dimensions: {face.dimensions} \n"
              f"Number of dlib Features: {len(face.features)} \n")
    else:
        print("Cannot find face!")


camera = Camera(format="OpenCV", flip_top_bottom=True)
face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")

camera.on_frame = find_faces

pause()
