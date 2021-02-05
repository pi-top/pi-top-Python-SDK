import json
from io import BytesIO
from flask import Flask, send_from_directory, Response
from flask_sockets import Sockets

from pitop import AlexRobot


# import decorators
app = Flask(__name__)
sockets = Sockets(app)


def parse_message(message):
    m = json.loads(message)
    m_type = m.get('type')
    m_data = m.get('data')

    m_type = m_type if isinstance(m_type, str) else ''
    m_data = m_data if isinstance(m_data, dict) else {}

    return m_type, m_data


@sockets.route('/command')
def command(ws):
    print('Command socket connected')
    while not ws.closed:
        message = ws.receive()
        if message:
            try:
                m_type, m_data = parse_message(message)
                handle_command(m_type, m_data)
            except Exception as e:
                print('Bad message: ', message, e)
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


def handle_command(m_type, data):
    if m_type == 'FORWARD':
        alex.forward(data['speed'])
    elif m_type == 'STOP':
        alex.stop()
    elif m_type == 'LEFT_MOTOR':
        alex.left(data['speed'])
    elif m_type == 'RIGHT_MOTOR':
        alex.right(data['speed'])
    else:
        print('Unrecognised command: ', m_type)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    alex = AlexRobot()
    alex.camera.on_frame = handle_frame
    frame_bytes = None

    print("Server starting on port 8070")
    server = pywsgi.WSGIServer(('', 8070), app, handler_class=WebSocketHandler)
    server.serve_forever()
