import flask
from packaging.version import Version


def uses_flask_1():
    return Version("2.0.0") > Version(flask.__version__) >= Version("1.0.0")
