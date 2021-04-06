from pitop import Camera
from signal import pause
from pitop.processing.algorithms.faces import FaceDetector, EmotionDetector
import cv2


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

    else:
        print("Face not found")


camera = Camera(format="OpenCV", flip_top_bottom=True)

face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")
emotion_detector = EmotionDetector(input_format="OpenCV", output_format="OpenCV")

camera.on_frame = frame_callback

pause()
