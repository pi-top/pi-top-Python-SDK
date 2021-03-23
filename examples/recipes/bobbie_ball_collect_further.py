# from further_link import send_image
from pitop import BobbieRobot
from signal import pause
from pitop.processing.algorithms import process_frame_for_ball
from pitop.core import ImageFunctions
import cv2
from time import sleep
import math


def capture_ball(ball_data):
    ball_center = ball_data.center

    if ball_center is None:
        # No objects detected for designated colour
        print("Colour not detected in frame")
    else:
        # coloured object detected
        x, y = ball_center
        radius = ball_data.radius
        bobbie.forward(0.15, hold=True)
        bobbie.target_lock_drive_angle(ball_data.angle)
        # print(f'y: {y} | width: {width}')
        if y < -90 and radius > 50:
            bobbie.pincer_controller.close()
            global ball_captured
            ball_captured = True


def deposit_ball():
    print('DEPOSITING BALL')
    global depositing_ball
    depositing_ball = True
    bobbie.stop()
    sleep(1)
    position = bobbie.position
    distance = math.sqrt(position.x**2 + position.y**2)
    theta = math.degrees(math.asin(position.y/distance))
    turn_angle = theta - position.angle - 180
    print(turn_angle)
    # turn_angle = turn_angle if turn_angle > -180 else turn_angle + 180
    # if turn_angle < -180:
    #     turn_angle = turn_angle + 180
    bobbie.rotate(turn_angle, 3)
    while True:
        position = bobbie.position
        # print(position)
        if position.x > 0.1:
            bobbie.forward(0.2)
        else:
            bobbie.stop()
            sleep(0.5)
            break
        sleep(0.1)
    bobbie.pincer_controller.open()
    sleep(1)
    bobbie.backward(0.2)
    sleep(0.5)
    bobbie.rotate(180, 3)
    bobbie.stop()
    # global ball_captured
    # ball_captured = False
    # depositing_ball = False


def process_frame(frame):
    if ball_captured:
        bobbie.camera.on_frame = None
        deposit_ball()
        robot_view = frame
    else:
        ball_data = process_frame_for_ball(frame, colours='red', image_return_format='opencv')
        robot_view = ball_data.robot_view
        capture_ball(ball_data)

    position = bobbie.position

    print(f'x: {position.x} | y: {position.y} | angle: {position.angle}')

    # bobbie.miniscreen.display_image(robot_view)

    # send_image(annotated_image)

    cv2.imshow("robot_view", robot_view)
    cv2.waitKey(1)


bobbie = BobbieRobot()
bobbie.calibrate()
bobbie.track_position()
ball_captured = False
depositing_ball = False
bobbie.pincer_controller.open()
bobbie.camera.on_frame = process_frame

pause()
