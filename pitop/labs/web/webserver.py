from flask import Flask, Response, send_from_directory, render_template
from flask_cors import CORS
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from pathlib import Path

from pitopcommon.sys_info import get_internal_ip
from pitopcommon.formatting import is_url


# TODO: get __main__.__file__ directory for template and static folders
def create_app(
        import_name='__main__',
        *args,
        template_folder=".",
        static_folder=".",
        **kargs):
    app = Flask(import_name, *args, template_folder=template_folder,
                static_folder=static_folder, **kargs)

    CORS(app)

    @app.route('/status')
    def status():
        return 'OK'

    @app.route('/', defaults={'path': 'index'})
    @app.route('/<path>')
    def send_file(path):
        if Path('./{}.html'.format(path)).is_file():
            return render_template('{}.html'.format(path))

        return send_from_directory('static', path)

    return app


class WebServer(WSGIServer):
    def __init__(self,
                 port=8070,
                 app=create_app()):
        self.port = port
        self.app = app
        self.sockets = Sockets(app)

        super().__init__(
            ('0.0.0.0', port),
            self.app,
            handler_class=WebSocketHandler)

    def _log_address(self):
        ip_addresses = list()
        for interface in ("wlan0", "ptusb0", "lo", "en0"):
            ip_address = get_internal_ip(interface)
            if is_url("http://" + ip_address):
                ip_addresses.append(ip_address)

        print("WebServer is listening at:")
        if len(ip_addresses) > 0:
            for ip_address in ip_addresses:
                print(f"\t- http://{ip_address}:{self.port}/")
        else:
            print(f"\t- http://localhost:{self.port}/ (on same device)")

    def start(self):
        self._log_address()
        super().start()
