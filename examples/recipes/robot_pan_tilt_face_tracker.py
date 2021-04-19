from pitop import Camera
from pitop.processing.algorithms.faces import FaceDetector
from pitop import Pitop, PanTiltController
from signal import pause
import cv2


def track_face(frame):
    face = face_detector.detect(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        face_center = face.center
        pan_tilt.track_object(face_center)
        print(f"Face center: {face_center}")
    else:
        pan_tilt.track_object.stop()
        print("Cannot find face!")


face_detector = FaceDetector()

pan_tilt = PanTiltController(servo_pan_port="S0", servo_tilt_port="S3")
pan_tilt.tilt_servo.target_angle = 0
pan_tilt.pan_servo.target_angle = 0

camera = Camera(resolution=(640, 480))
camera.on_frame = track_face

pause()
