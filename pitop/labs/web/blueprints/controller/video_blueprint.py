from flask import Blueprint, current_app
from pitop.labs.web.responses import VideoResponse


video_blueprint = Blueprint('video', __name__)


@video_blueprint.route('/video.mjpg')
def video():
    return VideoResponse(camera=current_app.config.get('camera'))
