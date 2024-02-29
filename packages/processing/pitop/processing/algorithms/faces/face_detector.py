import atexit
from os import getenv
from typing import Union

from imutils.video import FPS

from pitop.core import ImageFunctions
from pitop.processing.algorithms.faces.core.face import Face
from pitop.processing.core.load_models import load_face_landmark_predictor
from pitop.processing.core.vision_functions import (
    import_dlib,
    import_face_utils,
    import_imutils,
    import_opencv,
    tuple_for_color_by_name,
)

cv2 = None
dlib = None
imutils = None
face_utils = None


class FaceDetector:
    _FACE_DETECTOR_PYRAMID_LAYERS = (
        1  # set higher to detect smaller faces. Cost: large reduction in detection FPS.
    )

    def __init__(
        self,
        image_processing_width: Union[int, None] = 320,
        format: str = "OpenCV",
        enable_tracking: bool = True,
        dlib_landmark_predictor_filename: str = "shape_predictor_68_face_landmarks.dat",
    ):
        """:param Union[int, None] image_processing_width: image width to scale
        to for image processing, set to None for no scaling.

        :param str format: desired output image format.
        :param bool enable_tracking: enable dlib's correlaction tracker
            to track the detected face between frames.
        :param str dlib_landmark_predictor_filename: Filename for facial
            features predictor. Use 5 landmark version for slightly
            better performance whilst retaining ability to calculate
            face angle. May be incompatible with further processing e.g.
            emotion detection requires the 68-landmark version.
        """
        self.__import_libs()

        self._image_processing_width = image_processing_width
        self._format = format
        self._face_rectangle_detector = dlib.get_frontal_face_detector()
        self._predictor = load_face_landmark_predictor(
            model_filename=dlib_landmark_predictor_filename
        )
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
        """Detect a face in an image frame.

        :param frame: Image frame in OpenCV or PIL format.
        :return: Face object containing data about the detected face.
        """
        self.__import_libs()
        frame = ImageFunctions.convert(frame, format="OpenCV")

        if self._frame_scaler is None:
            _, width = frame.shape[0:2]
            self._frame_scaler = (
                width / self._image_processing_width
                if self._image_processing_width is not None
                else 1
            )

        frame_to_process = self.__get_frame_to_process(frame=frame)

        if self._face_tracker is None:
            # if the face tracker has not been started, we first need to use face detection to find a face
            face_rectangle, face_center, face_features = self.__detect_largest_face(
                frame=frame_to_process
            )
            if face_center is not None and self._enable_tracking:
                # Face found, enable dlib correlation tracker for subsequent calls
                self.__start_tracker(frame=frame_to_process, rectangle=face_rectangle)
        else:
            # We are in face tracking mode, use dlib correlation tracker to track the face
            face_rectangle, face_center, face_features = self.__track_face(
                frame=frame_to_process
            )
            if face_center is None:
                self.__stop_tracker()
                # attempt to detect face since tracker has failed
                face_rectangle, face_center, face_features = self.__detect_largest_face(
                    frame=frame_to_process
                )

        self.face = self.__prepare_face_data(
            frame=frame,
            face=self.face,
            rectangle=face_rectangle,
            center=face_center,
            features=face_features,
        )
        if self._print_fps:
            self._fps.update()

        return self.face

    def __import_libs(self):
        global cv2, dlib, imutils, face_utils
        if cv2 is None:
            cv2 = import_opencv()
        if dlib is None:
            dlib = import_dlib()
        if face_utils is None:
            face_utils = import_face_utils()
        if imutils is None:
            imutils = import_imutils()

    def __get_frame_to_process(self, frame):
        """Resize frame, convert to grayscale and use contrast limited adaptive
        histogram equalization (CLAHE) to improve the contrast of the image so
        that face features are more pronounced.

        :param frame: original frame from the camera in OpenCV format
        :return: OpenCV image to send to face processing algorithms
        """
        return self._clahe_filter.apply(
            cv2.cvtColor(
                imutils.resize(frame, width=self._image_processing_width),
                cv2.COLOR_BGR2GRAY,
            )
        )

    def __detect_largest_face(self, frame):
        """Use dlib face rectangle detector on the frame and process the
        detected rectangles to get the face data.

        :param frame: Image frame to process for faces
        :return: Detected face data
        """
        face_rectangle, face_center, face_features = self.__process_detected_rectangles(
            frame,
            self._face_rectangle_detector(frame, self._FACE_DETECTOR_PYRAMID_LAYERS),
        )

        return face_rectangle, face_center, face_features

    def __process_detected_rectangles(self, frame, rectangles_dlib):
        """Find largest face rectangle and process it to get the required face
        data.

        :param frame: OpenCV frame to use for processing
        :param rectangles_dlib: Rectangles found using dlib's face
            detector in the dlib Rectangle format.
        :return: Detected face data
        """
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

        face_features = self.__get_dlib_face_features(frame, largest_rectangle_dlib)

        return face_rectangle, face_center, face_features

    def __get_dlib_face_features(self, frame, dlib_rectangle):
        """Find's dlib face features using the predictor and then convert them
        to numpy format.

        :param frame: frame used to detect/track face rectangle.
        :param dlib_rectangle: Face rectangle in dlib Rectangle format.
        :return: 68x2 numpy array of x, y coordinates for facial
            features.
        """
        face_features_dlib = self._predictor(frame, dlib_rectangle)
        return face_utils.shape_to_np(face_features_dlib)

    def __start_tracker(self, frame, rectangle):
        self._face_tracker = dlib.correlation_tracker()
        self._face_tracker.start_track(
            frame,
            dlib.rectangle(
                rectangle[0],
                rectangle[1],
                rectangle[0] + rectangle[2],
                rectangle[1] + rectangle[3],
            ),
        )

    def __stop_tracker(self):
        self._face_tracker = None

    def __track_face(self, frame):
        """Use dlib correlation tracker to track the face from the last frame
        in the current frame.

        :param frame: OpenCV frame to use for processing
        :return: Face data
        """

        def convert_dlib_rect_to_int_type(rectangle):
            x_start = int(round(rectangle.left()))
            y_start = int(round(rectangle.top()))
            x_end = int(round(rectangle.right()))
            y_end = int(round(rectangle.bottom()))
            return dlib.rectangle(x_start, y_start, x_end, y_end)

        peak_to_side_lobe_ratio = self._face_tracker.update(frame)

        if peak_to_side_lobe_ratio < 7.0:
            # Object occluded or lost when PSR found to be below a certain threshold (7.0 according to Bolme et al)
            # Treat as failed attempt to track face and return
            return None, None, None

        rectangle_dlib = convert_dlib_rect_to_int_type(
            self._face_tracker.get_position()
        )
        face_features = self.__get_dlib_face_features(frame, rectangle_dlib)

        face_rectangle = face_utils.rect_to_bb(rectangle_dlib)
        face_center = (
            face_rectangle[0] + int(round(face_rectangle[2] / 2)),
            face_rectangle[1] + int(round(face_rectangle[3] / 2)),
        )

        return face_rectangle, face_center, face_features

    def __prepare_face_data(self, frame, face, rectangle, center, features):
        face.original_detection_frame = frame

        if center is None:
            face.clear()
            face.robot_view = ImageFunctions.convert(frame, format=self._format)
            return face

        # resize back to original frame resolution
        face.rectangle = tuple((int(item * self._frame_scaler) for item in rectangle))
        face.center_default = tuple((int(item * self._frame_scaler) for item in center))
        face.features = (features * self._frame_scaler).astype("int")

        face.robot_view = ImageFunctions.convert(
            self.__draw_on_frame(frame=frame.copy(), face=face), format=self._format
        )
        return face

    @staticmethod
    def __draw_on_frame(frame, face):
        x, y, w, h = face.rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            tuple_for_color_by_name("dodgerblue", bgr=True),
            2,
        )

        cv2.drawMarker(
            frame,
            face.center_default,
            tuple_for_color_by_name("orangered", bgr=True),
            markerType=cv2.MARKER_CROSS,
            markerSize=10,
            thickness=3,
            line_type=cv2.FILLED,
        )

        return frame

    def __print_fps(self):
        self._fps.stop()
        print(f"[INFO] Elapsed time: {self._fps.elapsed():.2f}")
        print(f"[INFO] Approx. FPS: {self._fps.fps():.2f}")
