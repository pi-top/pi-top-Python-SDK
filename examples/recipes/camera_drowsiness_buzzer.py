from signal import pause

from pitop.processing.algorithms.faces import FaceDetector

from pitop import Buzzer, Camera


def alert_on():
    buzzer.on()


def alert_off():
    global drowsy_counter
    drowsy_counter = 0
    buzzer.off()


def calculate_eye_aspect_ratio(face):
    left_eye_width, left_eye_height = face.left_eye_dimensions
    right_eye_width, right_eye_height = face.right_eye_dimensions

    left_eye_aspect_ratio = left_eye_height / left_eye_width
    right_eye_aspect_ratio = right_eye_height / right_eye_width

    eye_aspect_ratio_mean = (left_eye_aspect_ratio + right_eye_aspect_ratio) / 2

    return eye_aspect_ratio_mean


def find_faces(frame):
    global drowsy_counter
    face = face_detector(frame)

    if face.found:
        eye_aspect_ratio = calculate_eye_aspect_ratio(face)

        if eye_aspect_ratio < DROWSY_THRESHOLD:
            drowsy_counter += 1
            if drowsy_counter > ALERT_COUNT:
                alert_on()
        else:
            alert_off()
    else:
        buzzer.on() if lost_face_alert else buzzer.off()
        print("Cannot find face!")


camera = Camera(resolution=(640, 480), flip_top_bottom=True)
buzzer = Buzzer("D0")
face_detector = FaceDetector()

drowsy_counter = 0
DROWSY_THRESHOLD = 0.25
ALERT_COUNT = 10
lost_face_alert = False

camera.on_frame = find_faces

pause()
