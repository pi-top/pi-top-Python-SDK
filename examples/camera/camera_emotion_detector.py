from signal import pause

import cv2
from pitop import Camera
from pitop.processing.algorithms.faces import EmotionClassifier, FaceDetector


def detect_emotion(frame):
    face = face_detector(frame)
    emotion = emotion_classifier(face)

    if emotion.found:
        print(f"{emotion_lookup[emotion.type]}", end="\r", flush=True)
    else:
        print("Face not found!")

    cv2.imshow("Emotion", emotion.robot_view)
    cv2.waitKey(1)


camera = Camera(resolution=(640, 480), flip_top_bottom=True)

face_detector = FaceDetector()
emotion_classifier = EmotionClassifier()
emotion_types = emotion_classifier.emotion_types
ascii_emotions = [":|", ":c", "D:<", ":)", ":(", ":O"]
emotion_lookup = {
    emotion_types[i]: ascii_emotions[i] for i in range(len(emotion_types))
}

camera.on_frame = detect_emotion

pause()
