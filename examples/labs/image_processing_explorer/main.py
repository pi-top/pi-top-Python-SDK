from pitop import Camera
from pitop.processing.algorithms import BallDetector, process_frame_for_line
from pitop.labs import WebServer, MessagingBlueprint, VideoBlueprint

camera = Camera()
ball_detector = BallDetector(format="PIL")

selected_image_processor = 'line_detect'


def change_processor(new_image_processor):
    global selected_image_processor
    selected_image_processor = new_image_processor


def get_processed_frame():
    try:
        if selected_image_processor == 'line_detect':
            return process_frame_for_line(camera.current_frame()).robot_view

        if selected_image_processor == 'ball_detect':
            return ball_detector(camera.current_frame()).robot_view
    except:
        return b''


image_processing_explorer = WebServer(blueprints=[
    VideoBlueprint(name="raw_video", get_frame=camera.get_frame),
    VideoBlueprint(name="processed_video", get_frame=get_processed_frame),
    MessagingBlueprint(message_handlers={
                       'change_processor': change_processor}),
])

image_processing_explorer.serve_forever()
