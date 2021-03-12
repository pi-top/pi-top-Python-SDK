from pitop.camera import load_camera_cal
import cv2
import numpy as np
import math

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

CALIBRATION_RESOLUTION = (720, 1280)


class ArucoMarkers:

    def __init__(self, aruco_type: str = 'DICT_4X4_50', marker_size: int = 0.06):
        if aruco_type not in ARUCO_DICT.keys():
            raise ValueError('Invalid ArUco type.')
        self._aruco_dict = cv2.aruco.Dictionary_get(ARUCO_DICT[aruco_type])
        self._marker_size = marker_size
        self._aurco_params = cv2.aruco.DetectorParameters_create()
        self._mtx, self._dist = load_camera_cal()
        self._mtx_resolution_updated = False
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
        if not self._mtx_resolution_updated:
            frame_size = gray_frame.shape
            # print(frame_size)
            scale_factor_x = CALIBRATION_RESOLUTION[1] / frame_size[1]
            scale_factor_y = CALIBRATION_RESOLUTION[0] / frame_size[0]
            # print(scale_factor_x)
            # print(scale_factor_y)
            f_x = self._mtx[0][0] / scale_factor_x
            f_y = self._mtx[1][1] / scale_factor_y
            c_x = self._mtx[0][2] / scale_factor_x
            c_y = self._mtx[1][2] / scale_factor_y
            self._mtx[0][0] = f_x
            self._mtx[1][1] = f_y
            self._mtx[0][2] = c_x
            self._mtx[1][2] = c_y
            self._mtx_resolution_updated = True

        corners, ids, rejected = cv2.aruco.detectMarkers(gray_frame, self._aruco_dict, parameters=self._aurco_params)

        if len(corners) > 0:
            self._ids = ids
            # print(ids)
            self._corners = corners
            self._rotation_vectors, self._translation_vectors = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                                                                    self._marker_size,
                                                                                                    self._mtx,
                                                                                                    self._dist)

            self._marker_centers = self.__get_marker_centers(corners)

            # print(f'rvec: {self._rotation_vectors}')
            # print(f'tvec: {self._translation_vectors}')

            # print(f'distance: {distance}')
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

    def get_camera_pose(self):
        marker_poses = {}
        camera_poses = {}
        robot_pose_observation = np.array([[0, 0]])
        for marker_id, marker_rvec, marker_tvec in zip(self._ids, self._rotation_vectors, self._translation_vectors):
            rotation_matrix, _ = cv2.Rodrigues(marker_rvec)
            marker_pose = np.vstack((np.hstack((rotation_matrix, marker_tvec.T)), np.array([0, 0, 0, 1])))
            camera_pose = np.linalg.inv(marker_pose)
            # distance = np.sqrt(np.sum(marker_tvec ** 2))
            # print(distance)
            marker_poses[str(marker_id[0])] = marker_pose
            camera_poses[str(marker_id[0])] = camera_pose

            x = camera_pose[0][3]
            y = camera_pose[1][3]
            robot_pose_observation = np.array([[x, y]])
            print(robot_pose_observation)

        return robot_pose_observation

        # print(camera_poses)
        # print(f'marker_pose: {marker_pose}')
        # print(f'camera_pose: {camera_pose}')

        # {'[6]': array([[0.95522434, -0.12239293, 0.26938157, 0.14248621],
        #                [0.10365307, -0.71431859, -0.69210186, 0.20495458],
        #                [0.27713264, 0.68903477, -0.6696481, 0.38979999],
        #                [0., 0., 0., 1.]]),
        #  '[7]': array([[0.98732396, 0.11993919, -0.10395189, 0.16672809],
        #                [0.05623041, -0.87679297, -0.47756908, 0.10877701],
        #                [-0.14842353, 0.46567014, -0.87242293, 0.4600414],
        #                [0., 0., 0., 1.]])}

    @property
    def ids(self):
        return self._ids

    @property
    def centers(self):
        return self._marker_centers
