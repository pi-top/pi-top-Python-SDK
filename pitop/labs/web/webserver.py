from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from flask_sockets import Sockets
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from pitop.common.sys_info import get_internal_ip
from pitop.common.formatting import is_url

from .blueprints.base import BaseBlueprint


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
        try:
            return render_template(f'{path}.html')
        except Exception:
            return send_from_directory(app.static_folder, path)

    @app.after_request
    def add_header(req):
        req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        req.headers["Pragma"] = "no-cache"
        req.headers["Expires"] = "0"
        return req

    app.config['TEMPLATES_AUTO_RELOAD'] = True

    return app


class WebServer(WSGIServer):
    def __init__(
        self,
        port=8070,
        app=create_app(),
        blueprints=[BaseBlueprint()]
    ):
        self.port = port
        self.app = app
        self.sockets = Sockets(app)

        with self.app.app_context():
            for blueprint in blueprints:
                self.app.register_blueprint(blueprint, sockets=self.sockets)

        WSGIServer.__init__(
            self,
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
