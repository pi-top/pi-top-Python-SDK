from pitop.processing.algorithms.faces import FaceDetector, EmotionDetector
from pitop.processing.utils.vision_functions import import_opencv


cv2 = import_opencv()

face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")
emotion_detector = EmotionDetector(input_format="OpenCV", output_format="OpenCV")

count = 0
while count < 5:
    test_image = cv2.imread(f"images/image_{count}.jpg")

    face = face_detector.detect(test_image)
    emotion = emotion_detector.detect(face)
    if face.found:
        print(emotion.type, emotion.confidence)
        cv2.imshow("face", face.robot_view)
        cv2.imshow("emotion", emotion.robot_view)
        cv2.waitKey(0)
    count += 1

cv2.destroyAllWindows()