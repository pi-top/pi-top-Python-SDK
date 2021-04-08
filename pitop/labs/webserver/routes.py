import json
from io import BytesIO
from flask import (
    Response,
    current_app as app,
    send_from_directory,
)
from . import sockets
import gevent


@sockets.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            handle_command(message)
    print('Command socket disconnected')


def get_frame(camera):
    try:
        frame = camera.get_frame()
        buffered = BytesIO()
        frame.save(buffered, format="JPEG")
        return buffered.getvalue()
    except Exception as e:
        print(e)


@app.route('/video.mjpg')
def video():
    camera = app.config['robot'].camera
    pool = gevent.get_hub().threadpool

    def gen_frames(camera, pool):
        while True:
            # get_frame in thread so it won't block handler greenlets
            frame_bytes = pool.spawn(get_frame, camera).get()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )


    print('Video socket connected')
    return Response(
        gen_frames(camera, pool),
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
        robot.pan_tilt.pan_servo.target_angle = msg_data.get("angle", dict()).get("z")
        robot.pan_tilt.tilt_servo.target_angle = msg_data.get("angle", dict()).get("y")

    else:
        print(f"Unrecognised command: {msg_type}")
