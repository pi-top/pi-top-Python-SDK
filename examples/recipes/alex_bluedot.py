from bluedot import BlueDot
from pitop import AlexRobot
from signal import pause
from threading import Lock


bd = BlueDot()
bd.color = "#00B2A2"
alex = AlexRobot()


lock = Lock()


def move(pos):
    if lock.locked():
        return

    if any([
        pos.angle > 0 and pos.angle < 20,
        pos.angle < 0 and pos.angle > -20,
    ]):
        alex.forward(pos.distance, hold=True)
    elif pos.angle > 0 and 20 <= pos.angle <= 160:
        turn_radius = 0 if 70 < pos.angle < 110 else pos.distance
        speed_factor = -pos.distance if pos.angle > 110 else pos.distance
        alex.right(speed_factor, turn_radius)
    elif pos.angle < 0 and -160 <= pos.angle <= -20:
        turn_radius = 0 if -110 < pos.angle < -70 else pos.distance
        speed_factor = -pos.distance if pos.angle < -110 else pos.distance
        alex.left(speed_factor, turn_radius)
    elif any([
        pos.angle > 0 and pos.angle > 160,
        pos.angle < 0 and pos.angle < -160,
    ]):
        alex.backward(pos.distance, hold=True)


def stop(pos):
    lock.acquire()
    alex.stop()


def start(pos):
    if lock.locked():
        lock.release()
    move(pos)


bd.when_pressed = start
bd.when_moved = move
bd.when_released = stop

pause()
