from pitop.camera import Camera, load_camera_cal
from signal import pause
import cv2
import sys


def draw_axis(frame, rotation_vectors, translation_vectors):
    for marker_rvec, marker_tvec in zip(rotation_vectors, translation_vectors):
        cv2.aruco.drawAxis(frame, mtx, dist, marker_rvec, marker_tvec, 0.05)


def draw_markers(frame, ids, corners):
    cv2.aruco.drawDetectedMarkers(frame, corners)
    for marker_id, marker_corners in zip(ids, corners):
        top_left_corner = marker_corners[0][0]
        cv2.putText(frame, str(marker_id),
                    (int(top_left_corner[0]), int(top_left_corner[1] - 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (162, 178, 0), 2)


def get_marker_centers(corners):
    marker_centers = []
    for marker_corner in corners:
        corners = marker_corner.reshape((4, 2))
        top_left, top_right, bottom_right, bottom_left = corners
        c_x = int((top_left[0] + bottom_right[0]) / 2.0)
        c_y = int((top_left[1] + bottom_right[1]) / 2.0)
        marker_centers.append([c_x, c_y])

    return marker_centers


def aruco_detect(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = cv2.aruco.detectMarkers(gray_frame, aruco_dict, parameters=aurco_params)
    annotated_image = frame

    if len(corners) > 0:
        rotation_vectors, translation_vectors = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
        marker_centers = get_marker_centers(corners)
        draw_markers(annotated_image, ids, corners)
        draw_axis(annotated_image, rotation_vectors, translation_vectors)

    cv2.imshow("Image", annotated_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit()


camera = Camera(0, (640, 480), rotate_angle=0, format='opencv')
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
aurco_params = cv2.aruco.DetectorParameters_create()
mtx, dist = load_camera_cal()


camera.on_frame = aruco_detect


pause()
