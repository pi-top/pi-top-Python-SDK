from pitop.camera import Camera
from pitop.processing.algorithms import ArucoMarkers
from signal import pause
import cv2


def aruco_detect(frame):
    if aruco_markers.detect(frame):
        aruco_markers.draw_markers(frame)
        aruco_markers.draw_axis(frame)
        ids = aruco_markers.ids
        centers = aruco_markers.centers
        for id, center in zip(ids, centers):
            print(f'ID: {id} | Center: {center}')
    cv2.imshow("Image", frame)
    cv2.waitKey(1)


camera = Camera(0, (640, 480), rotate_angle=0, format='opencv')
aruco_markers = ArucoMarkers()
camera.on_frame = aruco_detect

pause()
