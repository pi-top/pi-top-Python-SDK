from pitop import DriveController, Camera
from pitop.labs import WebController

drive = DriveController()
camera = Camera()

speed = 0.2


def key_down(data):
    global speed

    key = data.get('key')
    if key == 'w':
        drive.forward(speed, hold=True)
    elif key == 's':
        drive.backward(speed, hold=True)
    elif key == 'd':
        drive.right(speed)
    elif key == 'a':
        drive.left(speed)
    elif key == 'ArrowUp':
        speed = speed if speed == 1 else speed + 0.2
    elif key == 'ArrowDown':
        speed = speed if speed == 0 else speed - 0.2


def key_up(data):
    key = data.get('key')
    if key == 'w' or key == 's':
        drive.stop()
    elif key == 'd':
        drive.right(0)
    elif key == 'a':
        drive.left(0)


controller = WebController(camera=camera, handlers={
    'key_down': key_down,
    'key_up': key_up
})

controller.serve_forever()
