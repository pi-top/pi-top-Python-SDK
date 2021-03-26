import os
import cv2
from pitop.processing.utils.vision_functions import find_largest_rectangle, resize
from pitop.core import ImageFunctions

# directory where calibration output pickle file is located
classifier_dir = 'classifiers'
script_dir = os.path.dirname(os.path.realpath(__file__))
abs_file_path = os.path.join(script_dir, classifier_dir)

# Filename for classifier
cascade_model_classifier = 'haarcascade_frontalface_default.xml'


class FaceDetector:
    def __init__(self):
        self._face_cascade = cv2.CascadeClassifier(os.path.join(abs_file_path, cascade_model_classifier))
        self._image_search_rectangle = None
        self._frame_resolution = None
        self._frame = None

    def face_detect(self, frame):

        cv_frame = ImageFunctions.convert(frame, format='OpenCV')

        cv_frame = resize(cv_frame, width=320)

        if self._frame_resolution is None:
            height, width = cv_frame.shape[0:2]
            self._frame_resolution = (width, height)

        gray = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2GRAY)

        if self._image_search_rectangle is not None:
            x, y, w, h = self._image_search_rectangle
            cropped_image = gray[y:y + h, x:x + w]
            faces = self._face_cascade.detectMultiScale(cropped_image, 1.1, 4)
            i = 0
            for x_f, y_f, w_f, h_f in faces:
                x_f = x_f + x
                y_f = y_f + y
                faces[i][0] = x_f
                faces[i][1] = y_f
                i += 1
        else:
            # if no faces previously found then we need to search whole image
            faces = self._face_cascade.detectMultiScale(gray, 1.1, 4)

        center,


    def process_faces(self, faces):
        if len(faces) != 0:
            largest_face = find_largest_rectangle(faces)
            self._image_search_rectangle = self.get_face_search_rectangle(largest_face)
            x, y, w, h = largest_face
            self._face_width = w
            face_centroid = (x + int(w/2), y + int(h/2))
            self.draw_robot_view(largest_face, face_centroid)
            face_centroid_repositioned = self.centroid_reposition(face_centroid)
            centroid_x, centroid_y = face_centroid_repositioned
            self._centroid_x_mean_array, centroid_x = running_mean(self._centroid_x_mean_array, centroid_x)
            self._centroid_y_mean_array, centroid_y = running_mean(self._centroid_y_mean_array, centroid_y)
            centroid = (centroid_x, centroid_y)
        else:
            self._image_search_rectangle = None
            centroid = (None, None)
            self._face_width = 0

        self._centroid = centroid

    def get_face_search_rectangle(self, rectangle):
        x, y, w, h = rectangle
        w_new = w * 2 if w * 2 < self._frame_resolution[0] else w
        h_new = h * 2 if h * 2 < self._frame_resolution[1] else h
        x_new = x - int((w_new - w)/2)
        y_new = y - int((h_new - h)/2)
        return x_new, y_new, w_new, h_new