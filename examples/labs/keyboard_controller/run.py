from pitop import Camera, DriveController, Pitop
from pitop.labs import WebController

robot = Pitop()
robot.add_component(DriveController())
robot.add_component(Camera())

speed = 0.2


def key_down(data, send):
    global speed

    key = data.get("key")
    if key == "w":
        robot.drive.forward(speed, hold=True)
    elif key == "s":
        robot.drive.backward(speed, hold=True)
    elif key == "d":
        robot.drive.right(speed)
    elif key == "a":
        robot.drive.left(speed)
    elif key == "ArrowUp":
        speed = min(1, speed + 0.2)
        send({"type": "speed", "data": speed})
    elif key == "ArrowDown":
        speed = max(0, speed - 0.2)
        send({"type": "speed", "data": speed})


def key_up(data):
    key = data.get("key")
    if key == "w" or key == "s":
        robot.drive.stop()
    elif key == "d":
        robot.drive.right(0)
    elif key == "a":
        robot.drive.left(0)


controller = WebController(
    get_frame=robot.camera.get_frame,
    message_handlers={"key_down": key_down, "key_up": key_up},
)

controller.serve_forever()
