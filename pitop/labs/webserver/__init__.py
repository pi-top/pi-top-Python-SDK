from flask import Flask
from flask_cors import CORS
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from pitopcommon.sys_info import get_internal_ip
from pitopcommon.formatting import is_url


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
        return app


def get_device_ip_addresses():
    ip_addresses = list()
    for interface in ("wlan0", "ptusb0", "lo"):
        ip_address = get_internal_ip(interface)
        if is_url("http://" + ip_address):
            ip_addresses.append(ip_address)
    return ip_addresses


def run_webserver(robot_instance, port=8070, serve_forever=True):
    for component in ("pan_tilt", "drive", "camera"):
        if not hasattr(robot_instance, component):
            raise AttributeError(f"Provided robot object needs to have a '{component}' component.")

    ip_addresses = get_device_ip_addresses()
    if len(ip_addresses) == 0:
        raise Exception("There are now available interfaces")

    print("Open a new tab in your browser and go to:")
    for ip_address in ip_addresses:
        print(f"\t- http://{ip_address}:{port}/")

    server = WSGIServer(
        ('0.0.0.0', port),
        create_app(robot_instance=robot_instance),
        handler_class=WebSocketHandler
    )
    if serve_forever:
        server.serve_forever()
    return server
