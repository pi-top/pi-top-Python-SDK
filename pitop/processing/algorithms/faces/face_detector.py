import dlib
from pitop.processing.core.vision_functions import center_reposition
from .face_utils import get_face_angle
from pitop.core import ImageFunctions
from imutils import (
    face_utils,
    resize,
)
from imutils.video import FPS
from os import (
    getenv,
    path
)
import atexit
from pitop.processing.core.vision_functions import (
    import_opencv,
    tuple_for_color_by_name,
)


cv2 = import_opencv()

predictor_dir = 'predictors'
script_dir = path.dirname(path.realpath(__file__))
abs_file_path = path.join(script_dir, predictor_dir)
predictor_file_name = "shape_predictor_68_face_landmarks.dat"


class Face:
    def __init__(self):
        self._center = None
        self._features = None
        self._angle = None
        self._rectangle = None
        self._robot_view = None
        self._original_frame = None

    def clear(self):
        self.center = None
        self.features = None
        self.angle = None
        self.rectangle = None

    @property
    def center(self):
        return center_reposition(self._center, self.original_detection_frame)

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        self._features = value

    @property
    def rectangle(self):
        return self._rectangle

    @rectangle.setter
    def rectangle(self, value):
        self._rectangle = value

    @property
    def robot_view(self):
        return self._robot_view

    @robot_view.setter
    def robot_view(self, value):
        self._robot_view = value

    @property
    def original_detection_frame(self):
        return self._original_frame

    @original_detection_frame.setter
    def original_detection_frame(self, value):
        self._original_frame = value

    @property
    def found(self) -> bool:
        """
        :return: Boolean to determine if a valid ball was found in the frame.
        :rtype: bool
        """
        return self.center is not None


class FaceDetector:
    def __init__(self, image_processing_width: int = 320, format: str = "OpenCV"):
        """
        :param image_processing_width: image width to scale to for image processing
        :param format: desired output image format
        """
        self._image_processing_width = image_processing_width
        self._format = format
        self._face_rectangle_detector = dlib.get_frontal_face_detector()
        self._predictor = dlib.shape_predictor(path.join(abs_file_path, predictor_file_name))
        self._clahe_filter = cv2.createCLAHE(clipLimit=5)
        self._frame_scaler = None
        self.face = Face()

        # Enable FPS if environment variable is set
        self._print_fps = getenv("PT_ENABLE_FPS", "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")

    def detect(self, frame):
        frame = ImageFunctions.convert(frame, format='OpenCV')

        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = width / self._image_processing_width

        self.face = self.__find_largest_face(face=self.face, frame=frame)

        if self._print_fps:
            self._fps.update()

        return self.face

    def __find_largest_face(self, face, frame):
        face.original_detection_frame = frame

        gray = self._clahe_filter.apply(
            cv2.cvtColor(
                resize(frame, width=self._image_processing_width),
                cv2.COLOR_BGR2GRAY
            )
        )

        face_rectangle, face_center, face_features = self.__process_rectangles(gray,
                                                                               self._face_rectangle_detector(gray, 0)
                                                                               )
        if face_rectangle is None:
            face.clear()
            face.robot_view = ImageFunctions.convert(frame, format=self._format)
            return face

        # resize back to original frame resolution
        face.rectangle = tuple((int(item * self._frame_scaler) for item in face_rectangle))
        face.center = tuple((int(item * self._frame_scaler) for item in face_center))
        face.features = (face_features * self._frame_scaler).astype("int")
        face.angle = get_face_angle(face.features)

        face.robot_view = ImageFunctions.convert(
            self.__draw_on_frame(frame=frame.copy(), face=face),
            format=self._format
        )

        return face

    def __process_rectangles(self, gray, rectangles_dlib):
        if len(rectangles_dlib) == 0:
            return None, None, None

        largest_rectangle_dlib = None
        area = 0
        face_rectangle = None
        face_center = None
        for rectangle_dlib in rectangles_dlib:
            x, y, w, h = face_utils.rect_to_bb(rectangle_dlib)
            current_area = w * h
            if current_area > area:
                area = current_area
                largest_rectangle_dlib = rectangle_dlib
                face_rectangle = (x, y, w, h)
                face_center = (int(x + w / 2), int(y + h / 2))

        if rectangles_dlib is None:
            # this should never trigger. Discuss.
            return None, None, None

        face_features_dlib = self._predictor(gray, largest_rectangle_dlib)
        face_features = face_utils.shape_to_np(face_features_dlib)

        return face_rectangle, face_center, face_features

    @staticmethod
    def __draw_on_frame(frame, face):
        x, y, w, h = face.rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), tuple_for_color_by_name("dodgerblue", bgr=True), 2)

        cv2.drawMarker(frame, face.center, tuple_for_color_by_name("orangered", bgr=True),
                       markerType=cv2.MARKER_CROSS, markerSize=10, thickness=3, line_type=cv2.FILLED)

        return frame
