from pitop.camera import load_camera_cal
import cv2

ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL
}


class ArucoMarkers:

    def __init__(self, aruco_type: str = 'DICT_4X4_50', marker_size: int = 0.05):
        if aruco_type not in ARUCO_DICT.keys():
            raise ValueError('Invalid ArUco type.')
        self._aruco_dict = cv2.aruco.Dictionary_get(ARUCO_DICT[aruco_type])
        self._marker_size = marker_size
        self._aurco_params = cv2.aruco.DetectorParameters_create()
        self._mtx, self._dist = load_camera_cal()
        self._ids = None
        self._rotation_vectors = None
        self._translation_vectors = None
        self._corners = None
        self._marker_centers = None

    def draw_axis(self, frame):
        if self._ids is not None:
            for marker_rvec, marker_tvec in zip(self._rotation_vectors, self._translation_vectors):
                cv2.aruco.drawAxis(frame, self._mtx, self._dist, marker_rvec, marker_tvec, 0.05)

    def draw_markers(self, frame):
        if self._ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, self._corners)
            for marker_id, marker_corners in zip(self._ids, self._corners):
                top_left_corner = marker_corners[0][0]
                cv2.putText(frame, str(marker_id),
                            (int(top_left_corner[0]), int(top_left_corner[1] - 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (162, 178, 0), 2)

    @staticmethod
    def __get_marker_centers(corners):
        marker_centers = []
        for marker_corner in corners:
            corners = marker_corner.reshape((4, 2))
            top_left, top_right, bottom_right, bottom_left = corners
            c_x = int((top_left[0] + bottom_right[0]) / 2.0)
            c_y = int((top_left[1] + bottom_right[1]) / 2.0)
            marker_centers.append([c_x, c_y])

        return marker_centers

    def detect(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray_frame, self._aruco_dict, parameters=self._aurco_params)

        if len(corners) > 0:
            self._ids = ids
            self._corners = corners
            self._rotation_vectors, self._translation_vectors = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                                                                    self._marker_size,
                                                                                                    self._mtx,
                                                                                                    self._dist)
            self._marker_centers = self.__get_marker_centers(corners)
            return True
        else:
            # set all data to None so it doesn't persist into other frames
            self.reset_data()
            return False

    def reset_data(self):
        self._rotation_vectors = None
        self._translation_vectors = None
        self._ids = None
        self._corners = None
        self._marker_centers = None

    @property
    def ids(self):
        return self._ids

    @property
    def centers(self):
        return self._marker_centers
