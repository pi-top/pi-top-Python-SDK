from flask import Blueprint, render_template, current_app as app, abort, Response
from gevent.event import Event

blueprint = Blueprint('controller', __name__,
                      template_folder='templates', static_folder='static')

frame_bytes = None
new_frame_event = Event()


def handle_frame(frame):
    try:
        buffered = BytesIO()
        frame.save(buffered, format="JPEG")
        global frame_bytes
        frame_bytes = buffered.getvalue()
        new_frame_event.set()
        new_frame_event.clear()
    except Exception:
        pass


@blueprint.route('/')
def index():
    return render_template('controller.html')


@blueprint.route('/video.mjpg')
def video():
    camera = app.config.get('camera', None)
    if camera is None:
        return abort(409)

    if camera.handle_frame is None:
        camera.handle_frame = handle_frame

    def frame_generator():
        while True:
            if new_frame_event.wait(timeout=0):
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )

    print('Video socket connected')
    return Response(
        frame_generator(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
