from pitop.processing.algorithms.faces import FaceDetector, FaceDetector2, emotion_classifier
import cv2
from imutils.convenience import resize

test_image = cv2.imread("images/test_1.jpg")
# test_image = cv2.imread("test_image.png")

face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")
# face_detector = FaceDetector2()

face = face_detector.detect(test_image)

prediction = emotion_classifier(face.features, face.dimensions)

print(prediction)

# cv2.imshow("robotview", face.robot_view)
cv2.imshow("robotview", resize(face.robot_view, width=320))
cv2.waitKey(0)
