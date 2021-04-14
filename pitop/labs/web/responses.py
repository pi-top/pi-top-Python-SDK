import gevent
from io import BytesIO
from flask import Response
from werkzeug.exceptions import HTTPException


class VideoResponse(Response):
    def __init__(self, camera=None, *args, **kwargs):
        if camera is None:
            raise HTTPException(409)

        def get_frame():
            try:
                frame = camera.get_frame()
                buffered = BytesIO()
                frame.save(buffered, format="JPEG")
                return buffered.getvalue()
            except Exception as e:
                print(e)

        def generate_frames():
            pool = gevent.get_hub().threadpool
            while True:
                # get_frame in thread so it won't block handler greenlets
                frame_bytes = pool.spawn(get_frame, camera).get()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n'+frame_bytes+b'\r\n'
                )

        Response.__init__(
            self,
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            **kwargs
         )

