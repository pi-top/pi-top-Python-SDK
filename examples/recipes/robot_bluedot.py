from signal import pause
from threading import Lock

from bluedot import BlueDot
from pitop import DriveController

bd = BlueDot()
bd.color = "#00B2A2"
lock = Lock()

drive = DriveController(left_motor_port="M3", right_motor_port="M0")


def move(pos):
    if lock.locked():
        return

    if any(
        [
            pos.angle > 0 and pos.angle < 20,
            pos.angle < 0 and pos.angle > -20,
        ]
    ):
        drive.forward(pos.distance, hold=True)
    elif pos.angle > 0 and 20 <= pos.angle <= 160:
        turn_radius = 0 if 70 < pos.angle < 110 else pos.distance
        speed_factor = -pos.distance if pos.angle > 110 else pos.distance
        drive.right(speed_factor, turn_radius)
    elif pos.angle < 0 and -160 <= pos.angle <= -20:
        turn_radius = 0 if -110 < pos.angle < -70 else pos.distance
        speed_factor = -pos.distance if pos.angle < -110 else pos.distance
        drive.left(speed_factor, turn_radius)
    elif any(
        [
            pos.angle > 0 and pos.angle > 160,
            pos.angle < 0 and pos.angle < -160,
        ]
    ):
        drive.backward(pos.distance, hold=True)


def stop(pos):
    lock.acquire()
    drive.stop()


def start(pos):
    if lock.locked():
        lock.release()
    move(pos)


bd.when_pressed = start
bd.when_moved = move
bd.when_released = stop

pause()
