"""
This example is for usage with the Prax robot configuration. The example does the following:
1. Prax will wait to be woken up by being patted on the head.
2. When woken, will try to detect a face. If a face is found Prax's head will copy the angle of the face.
3. When no face can be found within a number of cycles, Prax will go back to sleep by lowering its head.

Note: make sure to connect the Ultrasonic Sensor to port A1.
"""

from pitop import (
    Pitop,
    TiltRollHeadController,
    Camera,
    UltrasonicSensor,
)
from pitop.processing.algorithms.faces import FaceDetector
from time import sleep


def assemble_robot():
    pitop = Pitop()

    pitop.add_component(TiltRollHeadController())
    pitop.head.calibrate()

    pitop.add_component(Camera(resolution=(640, 480),
                               flip_top_bottom=True)
                        )

    pitop.add_component(UltrasonicSensor("A1"))

    return pitop


def wake_and_shake():
    robot.head.tilt.target_angle = 60
    robot.head.roll.target_angle = 0
    sleep(1)
    robot.head.shake()

    global awake
    awake = True


def go_to_sleep():
    robot.head.tilt.target_angle = 0
    robot.head.roll.target_angle = 0

    global awake
    awake = False


def detect_face():
    frame = robot.camera.get_frame()
    face = face_detector(frame)

    return face


def imitate_human():
    global face_lost_count

    face = detect_face()

    if face.found:
        face_lost_count = 0
        face_angle = face.angle
        robot.head.roll.target_angle = face_angle

    else:
        print("Face not found!")
        face_lost_count += 1
        if face_lost_count > 10:
            go_to_sleep()


def main():
    go_to_sleep()

    while True:
        if awake:
            imitate_human()
        else:
            distance = robot.ultrasonic.distance

            if distance < 0.05:
                pass
                wake_and_shake()

            sleep(0.1)


if __name__ == "__main__":
    robot = assemble_robot()
    face_detector = FaceDetector()

    awake = False
    face_lost_count = 0
    main()
