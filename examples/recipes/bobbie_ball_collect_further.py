# from further_link import send_image
from pitop import BobbieRobot
from signal import pause
from pitop.processing.algorithms import process_frame_for_object
from pitop.core import ImageFunctions
import cv2


def close_pincers():
    bobbie.left_pincer.target_angle = 0
    bobbie.right_pincer.target_angle = 0


def open_pincers():
    bobbie.left_pincer.target_angle = -45
    bobbie.right_pincer.target_angle = 45


def capture_ball(processed_frame):
    ball_center = processed_frame.object_center

    if ball_center is None:
        # No objects detected for designated colour
        print("Colour not detected in frame")
    else:
        # coloured object detected
        x, y = ball_center
        width, height = processed_frame.object_dimensions
        bobbie.forward(0.15, hold=True)
        bobbie.target_lock_drive_angle(processed_frame.angle)
        print(f'y: {y} | width: {width}')
        if y < -90 and width > 50:
            close_pincers()
            global ball_captured
            ball_captured = True


def deposit_ball(processed_frame):
    # deposit ball
    bobbie.stop()
    pass


def aruco_detect(frame):
    cv_frame = ImageFunctions.convert(frame, format="opencv")
    corners, ids, rejected = cv2.aruco.detectMarkers(cv_frame, arucoDict, parameters=arucoParams)
    annotated_image = cv_frame
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            # draw the bounding box of the ArUCo detection
            cv2.line(annotated_image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(annotated_image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(annotated_image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(annotated_image, bottomLeft, topLeft, (0, 255, 0), 2)
            # compute and draw the center (x, y)-coordinates of the ArUco
            # marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(annotated_image, (cX, cY), 4, (0, 0, 255), -1)
            # draw the ArUco marker ID on the image
            cv2.putText(annotated_image, str(markerID),
                        (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

    return annotated_image

def process_frame(frame):
    processed_frame = process_frame_for_object(frame)

    # annotated_image = aruco_detect(frame)


    # robot_view = processed_frame.robot_view

    # bobbie.miniscreen.display_image(robot_view)

    # send_image(annotated_image)
    # cv2.imshow("Image", annotated_image)
    # cv2.waitKey(0)
    # if ball_captured:
    #     # deposit ball at designated location
    #     deposit_ball(processed_frame)
    # else:
    #     capture_ball(processed_frame)

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
arucoParams = cv2.aruco.DetectorParameters_create()

bobbie = BobbieRobot()
bobbie.calibrate()
ball_captured = False

open_pincers()

bobbie.camera.on_frame = process_frame

pause()
