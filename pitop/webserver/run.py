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

    if msg_type == 'cmd_vel':
        linear_speed = msg_data.get("linear", dict()).get("x")
        angular_speed = msg_data.get("angular", dict()).get("z")
        alex.robot_move(linear_speed, angular_speed)

    elif msg_type == 'pan_tilt':
        alex.pan_servo.target_speed = msg_data.get("angular", dict()).get("z")
        alex.tilt_servo.target_speed = msg_data.get("angular", dict()).get("y")

    elif msg_type == 'servo_stop':
        servo_stop()

    else:
        print(f"Unrecognised command: {msg_type}")



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
