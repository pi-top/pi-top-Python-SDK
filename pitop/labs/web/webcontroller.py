from .webserver import WebServer
from .blueprints.controller import blueprint, socket_blueprint


class WebController(WebServer):
    def __init__(self, camera=None, handlers={}):
        super().__init__()

        self.app.config['handlers'] = handlers
        self.app.config['camera'] = camera

        with self.app.app_context():
            self.app.register_blueprint(blueprint)
            self.sockets.register_blueprint(socket_blueprint)
