from signal import pause

import cv2
from pitop import Camera
from pitop.processing.algorithms.faces import FaceDetector


def find_faces(frame):
    face = face_detector(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        print(
            f"Face angle: {face.angle} \n"
            f"Face center: {face.center} \n"
            f"Face rectangle: {face.rectangle} \n"
        )
    else:
        print("Cannot find face!")


camera = Camera(resolution=(640, 480), flip_top_bottom=True)
face_detector = FaceDetector()

camera.on_frame = find_faces

pause()
