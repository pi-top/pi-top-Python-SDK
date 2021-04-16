from pitop import Camera
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionDetector
)
from signal import pause
import cv2


def detect_emotion(frame):
    face = face_detector.detect(frame)
    emotion = emotion_detector.detect(face)

    cv2.imshow("Emotion", emotion.robot_view)
    cv2.waitKey(1)

    if emotion.found:
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


camera = Camera(flip_top_bottom=True)

face_detector = FaceDetector()
emotion_detector = EmotionDetector()

camera.on_frame = detect_emotion

pause()
