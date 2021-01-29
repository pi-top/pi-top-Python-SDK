from pitop import AlexRobot
from pitop.processing.algorithms.line_detect import process_frame_for_line

from signal import pause


# Set up robot
alex = AlexRobot()


# Set up logic based on line detection
def drive_based_on_frame(frame):
    processed_frame = process_frame_for_line(frame)
    print(f"Target angle: {processed_frame.angle:.2f} deg ", end="\r")
    alex.target_lock_drive_angle(processed_frame.angle)
    alex.miniscreen.display_image(processed_frame.robot_view)


# On each camera frame, detect a line
alex.camera.on_frame = drive_based_on_frame


pause()
