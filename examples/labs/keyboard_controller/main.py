from pitop import DriveController, Camera
from pitop.labs import WebController

drive = DriveController()
camera = Camera()


def key_down(data):
    key = data.get('key')
    if key == 'w':
        drive.forward(1, hold=True)
    elif key == 's':
        drive.backward(1, hold=True)
    elif key == 'd':
        drive.right(1)
    elif key == 'a':
        drive.left(1)


def key_up(data):
    key = data.get('key')
    if key == 'w' or key == 's':
        drive.stop()
    elif key == 'd':
        drive.right(1)
    elif key == 'a':
        drive.left(1)


controller = WebController(handlers={
    'key_down': key_down,
    'key_up': key_up
})

controller.serve_forever()
