import json
from io import BytesIO
from flask import Flask, send_from_directory, Response
from flask_sockets import Sockets

from pitop import AlexRobot


# import decorators
app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            # try:
            handle_command(message)

            # except Exception as e:
            #     print('Bad message: ', message, e)

    print('Command socket disconnected')


def handle_frame(frame):
    buffered = BytesIO()
    frame.save(buffered, format="JPEG", optimize=True)
    global frame_bytes
    frame_bytes = buffered.getvalue()


@app.route('/video.mjpg')
def video():
    def gen():
        while True:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    print('Video socket connected')
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


def handle_command(message):
    m = json.loads(message)

    msg_type = m.get('type', '')
    msg_data = m.get('data', dict()).get('data', dict())

    # print(msg_data)

    if msg_type == 'motor_move':

        motor_move(
            pos_x=msg_data.get("instance", dict()).get("frontPosition", dict()).get("x"),
            pos_y=msg_data.get("instance", dict()).get("frontPosition", dict()).get("y"),
        )

    elif msg_type == 'motor_stop':
        motor_stop()

    elif msg_type == 'servo_move':
        servo_move(
            angle=msg_data.get("angle", dict()).get("degree"),
            distance=msg_data.get("distance")
        )

    elif msg_type == 'servo_stop':
        servo_stop()

    else:
        print(f"Unrecognised command: {msg_type}")


def motor_move(pos_x, pos_y):
    x_speed_factor = abs(pos_x) / 100.0
    y_speed_factor = abs(pos_y) / 100.0

    # TODO: implement gradual left/right rotation
    turn_radius = 0

    if pos_x < 0:
        alex.left(x_speed_factor, turn_radius)
    elif pos_x > 0:
        alex.right(x_speed_factor, turn_radius)
    else:
        if pos_y < 0:
            alex.forward(y_speed_factor, hold=True)
        elif pos_y > 0:
            alex.backward(y_speed_factor, hold=True)


def motor_stop():
    alex.stop()


def servo_move(angle, distance):
    print(f"Servo move angle: {angle}")

    if 70 < angle < 110:

        print("TODO: Move tilt up")
        pass

    elif 0 <= angle <= 70 or 290 <= angle <= 360:

        print("TODO: Move pan right")
        pass

    elif 110 <= angle <= 250:

        print("TODO: Move pan left")
        pass

    elif 250 < angle < 290:

        print("TODO: Move tilt down")
        pass


def servo_stop():
    alex.stop()


if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler

    alex = AlexRobot()
    frame_bytes = None

    port = 8070

    alex.camera.on_frame = handle_frame

    print(f"Server starting on port {port}")
    try:
        WSGIServer(
            ('', port),
            app,
            handler_class=WebSocketHandler
        ).serve_forever()

    except KeyboardInterrupt:
        pass
