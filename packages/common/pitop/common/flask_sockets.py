# -*- coding: utf-8 -*-
# Taken from https://github.com/heroku-python/flask-sockets/
# Patched to work with werkzeug>=2.0.0

from werkzeug.routing import Map, Rule  # isort:skip
from werkzeug.exceptions import NotFound
from werkzeug.http import parse_cookie

try:
    from flask import request  # isort:skip
except ModuleNotFoundError:
    request = None


# Monkeys are made for freedom.
try:
    from geventwebsocket.gunicorn.workers import GeventWebSocketWorker as Worker
    from geventwebsocket.handler import WebSocketHandler
    from gunicorn.workers.ggevent import PyWSGIHandler

    import gevent  # noqa: F401, isort:skip
except ImportError:
    pass


def should_patch():
    import werkzeug
    from packaging.version import Version

    return Version(werkzeug.__version__) >= Version("2.0.0")


class SocketMiddleware(object):

    def __init__(self, wsgi_app, app, socket):
        self.ws = socket
        self.app = app
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        adapter = self.ws.url_map.bind_to_environ(environ)
        try:
            handler, values = adapter.match()
            environment = environ["wsgi.websocket"]
            cookie = None
            if "HTTP_COOKIE" in environ:
                cookie = parse_cookie(environ["HTTP_COOKIE"])

            with self.app.app_context():
                with self.app.request_context(environ):
                    if request:
                        # add cookie to the request to have correct session handling
                        request.cookie = cookie

                    handler(environment, **values)
                    return []
        except (NotFound, KeyError):
            return self.wsgi_app(environ, start_response)


class Sockets(object):

    def __init__(self, app=None):
        #: Compatibility with 'Flask' application.
        #: The :class:`~werkzeug.routing.Map` for this instance. You can use
        #: this to change the routing converters after the class was created
        #: but before any routes are connected.
        self.url_map = Map()

        #: Compatibility with 'Flask' application.
        #: All the attached blueprints in a dictionary by name. Blueprints
        #: can be attached multiple times so this dictionary does not tell
        #: you how often they got attached.
        self.blueprints = {}
        self._blueprint_order = []

        if should_patch():
            self.before_request_funcs = {}
            self.after_request_funcs = {}
            self.teardown_request_funcs = {}
            self.url_default_functions = {}
            self.url_value_preprocessors = {}
            self.template_context_processors = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        app.wsgi_app = SocketMiddleware(app.wsgi_app, app, self)

    def route(self, rule, **options):

        def decorator(f):
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f

        return decorator

    def add_url_rule(self, rule, _, f, **options):
        if should_patch():
            self.url_map.add(Rule(rule, endpoint=f, websocket=True))
        else:
            self.url_map.add(Rule(rule, endpoint=f))

    def register_blueprint(self, blueprint, **options):
        """Registers a blueprint for web sockets like for 'Flask' application.

        Decorator :meth:`~flask.app.setupmethod` is not applied, because it
        requires ``debug`` and ``_got_first_request`` attributes to be defined.
        """
        first_registration = False

        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, (
                "A blueprint's name collision occurred between %r and "
                '%r.  Both share the same name "%s".  Blueprints that '
                "are created on the fly need unique names."
                % (blueprint, self.blueprints[blueprint.name], blueprint.name)
            )
        else:
            first_registration = True
            if should_patch():
                self.template_context_processors[blueprint.name] = []
            else:
                self.blueprints[blueprint.name] = blueprint
                self._blueprint_order.append(blueprint)

        if not should_patch():
            blueprint.register(self, options, first_registration)
        elif first_registration:
            blueprint.register(self, options)


# CLI sugar.
if "Worker" in locals() and "PyWSGIHandler" in locals() and "gevent" in locals():

    class GunicornWebSocketHandler(PyWSGIHandler, WebSocketHandler):
        def log_request(self):
            if "101" not in self.status:
                super(GunicornWebSocketHandler, self).log_request()

    Worker.wsgi_handler = GunicornWebSocketHandler
    worker = Worker
