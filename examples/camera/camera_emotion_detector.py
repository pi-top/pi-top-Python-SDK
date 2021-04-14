from os import environ
from pitopcommon.current_session_info import get_first_display
from pitop import Camera
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionDetector
)
from signal import pause
from pitop.processing.core.vision_functions import import_opencv


cv2 = import_opencv()

environ["DISPLAY"] = get_first_display()


def frame_callback(frame):
    face = face_detector.detect(frame)
    emotion = emotion_detector.detect(face)

    cv2.imshow("Emotion", emotion.robot_view)
    cv2.waitKey(1)

    if face.found:
        if emotion.type == "Happy":
            print(":)")
        elif emotion.type == "Sad":
            print(":(")
        elif emotion.type == "Anger":
            print(":c")
        elif emotion.type == "Disgust":
            print("D:<")
        elif emotion.type == "Surprise":
            print(":O")
        elif emotion.type == "Neutral":
            print(":|")
    else:
        print("Face not found")


camera = Camera(format="OpenCV", flip_top_bottom=True)

face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")
emotion_detector = EmotionDetector(input_format="OpenCV", output_format="OpenCV")

camera.on_frame = frame_callback

pause()
