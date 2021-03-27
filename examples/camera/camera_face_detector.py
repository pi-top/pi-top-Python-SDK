from pitop import Camera
from pitop.processing.algorithms import FaceDetectorDLib
from signal import pause
import cv2


def find_faces(frame):
    face = face_detector.detect(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        print(f"Face center: {face.center}")
    else:
        print("Cannot find face!")


camera = Camera(format="OpenCV", rotate_angle=180)
face_detector = FaceDetectorDLib()

camera.on_frame = find_faces

pause()
