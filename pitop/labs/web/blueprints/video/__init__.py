import gevent
from io import BytesIO
from flask import Response, abort, Blueprint


class VideoResponse(Response):
    def __init__(self, video_feed=None, *args, **kwargs):
        if video_feed is None:
            abort(500, 'Unable to get frames')

        def _video_feed():
            try:
                frame = video_feed()
                buffered = BytesIO()
                frame.save(buffered, format="JPEG")
                return buffered.getvalue()
            except Exception as e:
                print(e)

        def generate_frames():
            pool = gevent.get_hub().threadpool
            while True:
                # video_feed in thread so it won't block handler greenlets
                frame_bytes = pool.spawn(_video_feed).get()
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


class VideoBlueprint(Blueprint):
    def __init__(self, name="video", video_feed=None, **kwargs):
        Blueprint.__init__(
            self,
            name,
            __name__,
            static_folder="video",
            **kwargs
        )

        @self.route(f"/{name}.mjpg")
        def video():
            return VideoResponse(video_feed=video_feed)
