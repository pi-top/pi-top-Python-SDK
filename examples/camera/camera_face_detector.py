from pitop import Camera
from pitop.processing.algorithms.faces import FaceDetector, emotion_classifier
from signal import pause
from imutils.convenience import resize
import cv2


def find_faces(frame):
    face = face_detector.detect(frame)
    robot_view = face.robot_view

    cv2.imshow("Faces", resize(robot_view, width=640))
    cv2.waitKey(1)

    if face.found:
        # print(f"Face angle: {face.angle} \n"
        #       f"Face center: {face.center} \n"
        #       f"Face dimensions: {face.dimensions} \n"
        #       f"Number of dlib Features: {len(face.features)} \n")
        emotion = emotion_classifier(face.features, face.dimensions)
        if emotion.confidence > 0.4:
            print(emotion.type, emotion.confidence)
    else:
        pass
        # print("Cannot find face!")


camera = Camera(format="OpenCV", flip_top_bottom=True)
face_detector = FaceDetector(input_format="OpenCV", output_format="OpenCV")

camera.on_frame = find_faces

pause()
