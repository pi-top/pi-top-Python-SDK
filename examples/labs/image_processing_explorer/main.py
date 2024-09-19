from pitop import Camera
from pitop.labs import MessagingBlueprint, VideoBlueprint, WebServer
from pitop.processing.algorithms import BallDetector, process_frame_for_line

camera = Camera()
ball_detector = BallDetector(format="PIL")

selected_image_processor = "blue_line_detect"

green_hsv_limits = ([60, 100, 100], [80, 255, 255])
red_hsv_limits = ([0, 100, 100], [10, 255, 255])


def change_processor(new_image_processor):
    global selected_image_processor
    selected_image_processor = new_image_processor


def get_processed_frame():
    try:
        if selected_image_processor == "blue_line_detect":
            return process_frame_for_line(frame=camera.current_frame()).robot_view
        elif selected_image_processor == "red_line_detect":
            return process_frame_for_line(
                frame=camera.current_frame(), hsv_limits=red_hsv_limits
            ).robot_view
        elif selected_image_processor == "green_line_detect":
            return process_frame_for_line(
                frame=camera.current_frame(), hsv_limits=green_hsv_limits
            ).robot_view
        elif selected_image_processor == "ball_detect":
            return ball_detector(camera.current_frame()).robot_view
    except Exception:
        return b""


image_processing_explorer = WebServer(
    blueprints=[
        VideoBlueprint(name="raw_video", get_frame=camera.get_frame),
        VideoBlueprint(name="processed_video", get_frame=get_processed_frame),
        MessagingBlueprint(message_handlers={"change_processor": change_processor}),
    ]
)

image_processing_explorer.serve_forever()
