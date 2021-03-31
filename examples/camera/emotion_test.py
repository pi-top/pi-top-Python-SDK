from pitop.processing.algorithms.faces import FaceDetector, emotion_classifier
import cv2

face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")

count = 0
while count < 7:
    test_image = cv2.imread(f"images/test_{count}.jpg")

    face = face_detector.detect(test_image)
    if face.found:
        emotion = emotion_classifier(face.features, face.dimensions)
        print(emotion.type, emotion.confidence)
        cv2.imshow("robotview", face.robot_view)
        cv2.waitKey(0)
    count += 1

cv2.destroyAllWindows()
