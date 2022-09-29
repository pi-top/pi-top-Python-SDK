from signal import pause

import cv2
from pitop import Camera, Pitop, TiltRollHeadController
from pitop.processing.algorithms.faces import FaceDetector


def track_face(frame):
    face = face_detector(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        face_angle = face.angle
        robot.head.track_head_angle(face_angle)
        print(f"Face angle: {face.angle}")
    else:
        robot.head.roll.sweep(speed=0)
        print("Cannot find face!")


robot = Pitop()

robot.add_component(TiltRollHeadController(servo_roll_port="S0", servo_tilt_port="S3"))
robot.head.calibrate()
robot.head.tilt.target_angle = 70
robot.head.roll.target_angle = 0

robot.add_component(Camera(resolution=(640, 480), flip_top_bottom=True))

face_detector = FaceDetector()

robot.camera.on_frame = track_face

pause()
