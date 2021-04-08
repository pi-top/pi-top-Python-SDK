import gevent
from flask import Blueprint, render_template, current_app as app, abort, Response
from io import BytesIO

blueprint = Blueprint('controller', __name__,
                      template_folder='templates', static_folder='static')


def get_frame(camera):
    try:
        frame = camera.get_frame()
        buffered = BytesIO()
        frame.save(buffered, format="JPEG")
        return buffered.getvalue()
    except Exception as e:
        print(e)


@blueprint.route('/')
def index():
    return render_template('controller.html')


@blueprint.route('/video.mjpg')
def video():
    pool = gevent.get_hub().threadpool
    camera = app.config.get('camera', None)
    if camera is None:
        return abort(409)

    def generate_frames():
        while True:
            # get_frame in thread so it won't block handler greenlets
            frame_bytes = pool.spawn(get_frame, camera).get()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    print('Video socket connected')
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
