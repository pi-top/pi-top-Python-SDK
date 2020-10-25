from enum import Enum

from .store_frame import StoreFrame
from .video_capture import VideoCapture
from .motion_detector import MotionDetector
from .generic_action import GenericAction


class CaptureActions(Enum):
    CAPTURE_SINGLE_FRAME = StoreFrame
    CAPTURE_VIDEO_TO_FILE = VideoCapture
    DETECT_MOTION = MotionDetector
    HANDLE_FRAME = GenericAction
