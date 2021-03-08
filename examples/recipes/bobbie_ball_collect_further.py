from further_link import send_image
from pitop import BobbieRobot
from signal import pause
from pitop.processing.algorithms import process_frame_for_object


def close_pincers():
    bobbie.left_pincer.target_angle = 0
    bobbie.right_pincer.target_angle = 0


def open_pincers():
    bobbie.left_pincer.target_angle = -45
    bobbie.right_pincer.target_angle = 45


def capture_ball(processed_frame):
    ball_center = processed_frame.object_center

    if ball_center is None:
        # No objects detected for designated colour
        print("Colour not detected in frame")
    else:
        # coloured object detected
        x, y = ball_center
        width, height = processed_frame.object_dimensions
        bobbie.forward(0.15, hold=True)
        bobbie.target_lock_drive_angle(processed_frame.angle)
        print(f'y: {y} | width: {width}')
        if y < -90 and width > 50:
            close_pincers()
            global ball_captured
            ball_captured = True


def deposit_ball(processed_frame):
    # deposit ball
    bobbie.stop()
    pass


def process_frame(frame):
    processed_frame = process_frame_for_object(frame)

    robot_view = processed_frame.robot_view

    bobbie.miniscreen.display_image(robot_view)

    send_image(robot_view)

    if ball_captured:
        # deposit ball at designated location
        deposit_ball(processed_frame)
    else:
        capture_ball(processed_frame)


bobbie = BobbieRobot()
bobbie.calibrate()
ball_captured = False

open_pincers()

bobbie.camera.on_frame = process_frame

pause()
