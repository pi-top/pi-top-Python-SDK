from signal import pause
from time import sleep
from datetime import datetime
import pygame

from pitop import Camera, DriveController, Pitop, PanTiltController, Button
from pitop.processing.algorithms.line_detect import process_frame_for_line

# Assemble a robot
robot = Pitop()
robot.add_component(DriveController(left_motor_port="M3", right_motor_port="M0"))
robot.add_component(PanTiltController(servo_pan_port="S0", servo_tilt_port="S3"))
robot.add_component(Camera())
robot.add_component(Button("D0"))

#Point camera down to look for line to follow
robot.pan_tilt.tilt_servo.target_angle = 40
robot.pan_tilt.pan_servo.target_angle = 0
print("camera moved to face down")

#Set up audio
pygame.mixer.init()
pygame.mixer.music.set_volume(1)  # quiet for testing late at night
pygame.mixer.music.load("coffee_request_2.ogg")
#pygame.mixer.music.play()
# while pygame.mixer.music.get_busy():
#    continue

#haveLine = True
last_motion_detected = None

def follow_the_line():
    while True:

    # Set up logic based on line detection
    #def drive_based_on_frame(frame):
        processed_frame = process_frame_for_line(robot.camera.get_frame())

        if processed_frame.line_center is None:
            #print("Line is lost!", end="\r")
            print("Couldn't find any more line!")
            #haveLine = False
            robot.drive.target_lock_drive_angle(0)
            robot.drive.forward(0, hold=False)
            robot.drive.stop_rotation()
            robot.drive.stop()
            sleep(1)
            break
        else:
            #print(f"Target angle: {processed_frame.angle:.2f} deg ", end="\r")
            robot.drive.forward(0.25, hold=True)
            robot.drive.target_lock_drive_angle(processed_frame.angle)
            robot.miniscreen.display_image(processed_frame.robot_view)

        #also possible to break from this loop by pressing the button
        if robot.button.is_pressed is True:  # When button is pressed it will return True
            print("button pressed")
            break

follow_the_line()

## On each camera frame, detect a line
#robot.camera.on_frame = drive_based_on_frame

#Turn around
robot.drive.rotate(180,1)

#Point camera up to look for people moving around
robot.pan_tilt.tilt_servo.target_angle = -50
robot.pan_tilt.pan_servo.target_angle = 0
sleep(3)
print("camera moved to face up")

#Next step, ask for coffee and wait for button press
def motion_detected():
    print("Motion detected")
    if pygame.mixer.music.get_busy():#do nothing if sound is already playing
        return
    pygame.mixer.music.play()#request coffee

print("Motion detector starting...")
robot.camera.start_detecting_motion(
    callback_on_motion=motion_detected, moving_object_minimum_area=100#350
)

while True:
    if robot.button.is_pressed is True:  # When button is pressed it will return True
        print("button pressed")
        break

robot.camera.stop_detecting_motion()
print("Motion detector stopped")
pygame.mixer.music.load("coffee_thankyou_1.ogg")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    sleep(0.1)

#resume line following
print("resume line following")
#Point camera down to look for line to follow
robot.pan_tilt.tilt_servo.target_angle = 40
robot.pan_tilt.pan_servo.target_angle = 0
sleep(3)
print("camera moved to face down")

follow_the_line()


pause()







#def motion_detected():
    #global last_motion_detected
 #   print("Motion detected")
    #do nothing if sound is already playing or it hasn't been a minimum of XX seconds
  #  if pygame.mixer.music.get_busy(): #or (datetime.now().timestamp() - last_motion_detected) < 10:
   #     return
    #request coffee
    #pygame.mixer.music.play()
#    if robot.camera.is_recording() is False:
#        print("Motion detected! Starting recording...")
#        output_file_name = f"/home/pi/Desktop/My Motion Recording {strftime('%Y-%m-%d %H:%M:%S', localtime(last_motion_detected))}.avi"
#        cam.start_video_capture(output_file_name=output_file_name)
#        while (datetime.now().timestamp() - last_motion_detected) < 10:
#            sleep(1)
#        cam.stop_video_capture()
#        print(f"Recording completed - saved to {output_file_name}")
    #last_motion_detected = datetime.now().timestamp()

pause()
