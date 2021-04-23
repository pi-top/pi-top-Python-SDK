import gevent
from io import BytesIO
from flask import Response, abort, Blueprint


class VideoResponse(Response):
    def __init__(self, video_input=None, *args, **kwargs):
        if video_input is None:
            abort(500, 'Unable to get frames')

        def _video_input():
            try:
                frame = video_input()
                buffered = BytesIO()
                frame.save(buffered, format="JPEG")
                return buffered.getvalue()
            except Exception as e:
                print(e)

        def generate_frames():
            pool = gevent.get_hub().threadpool
            while True:
                # video_input in thread so it won't block handler greenlets
                frame_bytes = pool.spawn(_video_input).get()
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
    def __init__(self, name="video", video_input=None, **kwargs):
        Blueprint.__init__(
            self,
            name,
            __name__,
            static_folder="video",
            **kwargs
        )

        @self.route(f"/{name}.mjpg")
        def video():
            return VideoResponse(video_input=video_input)
