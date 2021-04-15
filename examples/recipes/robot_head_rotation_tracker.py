from pitop import Camera
from pitop.processing.algorithms.faces import FaceDetector
from pitop import Pitop, TiltRollHeadController
from signal import pause
from pitop.processing.core.vision_functions import import_opencv

cv2 = import_opencv()


def track_face(frame):
    face = face_detector.detect(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", robot_view)
    cv2.waitKey(1)

    if face.found:
        face_angle = face.angle
        robot.tilt_roll.track_head_angle(face_angle)
        print(f"Face angle: {face.angle}")
    else:
        robot.tilt_roll.roll_servo.sweep(speed=0)
        print("Cannot find face!")


robot = Pitop()

robot.add_component(TiltRollHeadController(servo_roll_port="S0", servo_tilt_port="S3"))
robot.tilt_roll.calibrate()
robot.tilt_roll.tilt_servo.target_angle = 70
robot.tilt_roll.roll_servo.target_angle = 0

robot.add_component(Camera(format="OpenCV", flip_top_bottom=True))

face_detector = FaceDetector(input_format="OpenCV", format="OpenCV")

robot.camera.on_frame = track_face

pause()
