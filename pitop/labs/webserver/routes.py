import json
from io import BytesIO
from flask import (
    Response,
    current_app as app,
    send_from_directory,
)
from . import sockets


@sockets.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            handle_command(message)
    print('Command socket disconnected')


@app.route('/video.mjpg')
def video():
    robot = app.config['robot']

    def gen():
        while True:
            try:
                frame = robot.camera.get_frame()
                buffered = BytesIO()
                frame.save(buffered, format="JPEG", optimize=True, quality=30)
                frame_bytes = buffered.getvalue()

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )
            except Exception:
                pass

    print('Video socket connected')
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/')
def root():
    return send_static_file('index.html')


@app.route('/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


def handle_command(message):
    m = json.loads(message)

    msg_type = m.get('type', '')
    msg_data = m.get('data', dict()).get('data', dict())
    robot = app.config['robot']

    if msg_type == 'cmd_vel':
        linear_speed = msg_data.get("linear", dict()).get("x")
        angular_speed = msg_data.get("angular", dict()).get("z")
        robot.drive.robot_move(linear_speed, angular_speed)

    elif msg_type == 'pan_tilt':
        conversion_factor = 90.0 / 100.0
        robot.pan_tilt.pan_servo.target_angle = msg_data.get("angular", dict()).get("z") * conversion_factor
        robot.pan_tilt.tilt_servo.target_angle = msg_data.get("angular", dict()).get("y") * conversion_factor

    else:
        print(f"Unrecognised command: {msg_type}")
