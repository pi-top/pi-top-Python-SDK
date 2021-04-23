from pitop import DriveController, Camera
from pitop.labs import WebController

drive = DriveController()
camera = Camera()

speed = 0.2


def key_down(data, send):
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
        speed = min(1, speed + 0.2)
        send({'type': 'speed', 'data': speed})
    elif key == 'ArrowDown':
        speed = max(0, speed - 0.2)
        send({'type': 'speed', 'data': speed})


def key_up(data):
    key = data.get('key')
    if key == 'w' or key == 's':
        drive.stop()
    elif key == 'd':
        drive.right(0)
    elif key == 'a':
        drive.left(0)


controller = WebController(video_input=camera.get_frame, message_handlers={
    'key_down': key_down,
    'key_up': key_up
})

controller.serve_forever()
