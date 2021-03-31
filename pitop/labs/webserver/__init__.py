from flask import Flask
from flask_cors import CORS
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler


sockets = None


def create_app(robot_instance):
    app = Flask(__name__,
                static_url_path='',
                static_folder='./static')
    global sockets
    sockets = Sockets(app)

    CORS(app)

    with app.app_context():
        from . import routes  # noqa: F401
        app.config['robot'] = robot_instance
        robot_instance.camera.on_frame = routes.handle_frame
        return app


def run_webserver(robot_instance, port=8070, serve_forever=True):
    print(f"\n\nOpen a new tab in your browser and go to http://127.0.0.1:{port}/")

    server = WSGIServer(
        ('0.0.0.0', port),
        create_app(robot_instance=robot_instance),
        handler_class=WebSocketHandler
    )
    if serve_forever:
        server.serve_forever()
    return server
