import flask
from packaging.version import Version


def uses_flask_2():
    return Version("3.0.0") > Version(flask.__version__) >= Version("2.0.0")
