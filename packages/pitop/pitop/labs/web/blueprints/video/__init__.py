from io import BytesIO

import gevent
from flask import Blueprint, Response, abort


class VideoResponse(Response):
    def __init__(self, get_frame=None, *args, **kwargs):
        if get_frame is None:
            abort(500, "Unable to get frames")

        def _get_frame():
            try:
                frame = get_frame()
                buffered = BytesIO()
                frame.save(buffered, format="JPEG")
                return buffered.getvalue()
            except Exception as e:
                print(e)

        def generate_frames():
            pool = gevent.get_hub().threadpool
            while True:
                # get_frame in thread so it won't block handler greenlets
                frame_bytes = pool.spawn(_get_frame).get()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

        Response.__init__(
            self,
            generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
            **kwargs,
        )


class VideoBlueprint(Blueprint):
    def __init__(self, name="video", get_frame=None, **kwargs):
        Blueprint.__init__(
            self,
            name,
            __name__,
            static_folder="video",
            template_folder="templates",
            **kwargs,
        )

        @self.route(f"/{name}.mjpg")
        def video():
            return VideoResponse(get_frame=get_frame)
