import dlib
from typing import Union
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
        return center_reposition(self._center, self.original_detection_frame) if self._center is not None else None

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def center_top_left_zero(self):
        return self._center

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
    _FACE_DETECTOR_PYRAMID_LAYERS = 1  # set higher to detect smaller faces. Cost: large reduction in detection FPS

    def __init__(self,
                 image_processing_width: Union[int, None] = 320,
                 format: str = "OpenCV",
                 enable_tracking: bool = True):
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
        self._enable_tracking = enable_tracking
        self._face_tracker = None

        # Enable FPS if environment variable is set
        self._print_fps = getenv("PT_ENABLE_FPS", "0") == "1"
        if self._print_fps:
            self._fps = FPS().start()
            atexit.register(self.__print_fps)

    def __call__(self, frame):
        frame = ImageFunctions.convert(frame, format='OpenCV')

        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = width / self._image_processing_width if self._image_processing_width is not None else 1

        frame_to_process = self.__get_frame_to_process(frame=frame)

        if self._face_tracker is None:
            face_rectangle, face_center, face_features = self.__detect_largest_face(frame=frame_to_process)
            if face_center is not None and self._enable_tracking:
                self.__start_tracker(frame=frame_to_process, rectangle=face_rectangle)
        else:
            face_rectangle, face_center, face_features = self.__track_face(frame=frame_to_process)
            if face_center is None:
                self.__stop_tracker()
                # attempt to detect face again
                face_rectangle, face_center, face_features = self.__detect_largest_face(frame=frame_to_process)

        self.face = self.__prepare_face_data(frame=frame,
                                             face=self.face,
                                             rectangle=face_rectangle,
                                             center=face_center,
                                             features=face_features)
        if self._print_fps:
            self._fps.update()

        return self.face

    def __get_frame_to_process(self, frame):
        return self._clahe_filter.apply(
            cv2.cvtColor(
                resize(frame, width=self._image_processing_width),
                cv2.COLOR_BGR2GRAY
            )
        )

    def __detect_largest_face(self, frame):
        face_rectangle, face_center, face_features = self.__process_detected_rectangles(
            frame,
            self._face_rectangle_detector(frame, self._FACE_DETECTOR_PYRAMID_LAYERS)
        )

        return face_rectangle, face_center, face_features

    def __start_tracker(self, frame, rectangle):
        self._face_tracker = dlib.correlation_tracker()
        self._face_tracker.start_track(frame,
                                       dlib.rectangle(
                                           rectangle[0],
                                           rectangle[1],
                                           rectangle[0] + rectangle[2],
                                           rectangle[1] + rectangle[3]
                                       )
                                       )

    def __stop_tracker(self):
        self._face_tracker = None

    def __track_face(self, frame):
        def convert_dlib_rect_to_int_type(rectangle):
            x_start = int(round(rectangle.left()))
            y_start = int(round(rectangle.top()))
            x_end = int(round(rectangle.right()))
            y_end = int(round(rectangle.bottom()))
            return dlib.rectangle(x_start, y_start, x_end, y_end)

        peak_to_side_lobe_ratio = self._face_tracker.update(frame)

        if peak_to_side_lobe_ratio < 7.0:
            # Object occluded or lost when PSR found to be below a certain threshold (7.0 according to Bolme et al)
            return None, None, None

        rectangle_dlib = convert_dlib_rect_to_int_type(self._face_tracker.get_position())
        face_features_dlib = self._predictor(frame, rectangle_dlib)
        face_features = face_utils.shape_to_np(face_features_dlib)

        face_rectangle = face_utils.rect_to_bb(rectangle_dlib)
        face_center = (face_rectangle[0] + int(round(face_rectangle[2] / 2)),
                       face_rectangle[1] + int(round(face_rectangle[3] / 2)))

        return face_rectangle, face_center, face_features

    def __prepare_face_data(self, frame, face, rectangle, center, features):
        face.original_detection_frame = frame

        if center is None:
            face.clear()
            face.robot_view = ImageFunctions.convert(frame, format=self._format)
            return face

        # resize back to original frame resolution
        face.rectangle = tuple((int(item * self._frame_scaler) for item in rectangle))
        face.center = tuple((int(item * self._frame_scaler) for item in center))
        face.features = (features * self._frame_scaler).astype("int")
        face.angle = get_face_angle(face.features)

        face.robot_view = ImageFunctions.convert(
            self.__draw_on_frame(frame=frame.copy(), face=face),
            format=self._format
        )
        return face

    def __process_detected_rectangles(self, gray, rectangles_dlib):
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

        cv2.drawMarker(frame, face.center_top_left_zero, tuple_for_color_by_name("orangered", bgr=True),
                       markerType=cv2.MARKER_CROSS, markerSize=10, thickness=3, line_type=cv2.FILLED)

        return frame

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")
