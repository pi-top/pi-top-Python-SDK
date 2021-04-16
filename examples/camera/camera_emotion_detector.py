from pitop import Camera
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionDetector
)
from signal import pause
import cv2
import sys


def detect_emotion(frame):
    face = face_detector.detect(frame)
    emotion = emotion_detector.detect(face)

    if emotion.found:
        print(f"{emotion_lookup[emotion.type]}")
    else:
        print("Face not found!")

    cv2.imshow("Emotion", emotion.robot_view)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        camera.on_frame = None
        cv2.destroyAllWindows()
        sys.exit()


camera = Camera(resolution=(640, 480), flip_top_bottom=True)

face_detector = FaceDetector()
emotion_detector = EmotionDetector()
emotion_types = emotion_detector.emotion_types
ascii_emotions = [":|", ":c", "D:<", ":)", ":(", ":O"]
emotion_lookup = {emotion_types[i]: ascii_emotions[i] for i in range(len(emotion_types))}

camera.on_frame = detect_emotion

pause()
