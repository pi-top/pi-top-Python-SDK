from pitop import Pitop, Camera
from PIL import Image, ImageFont, ImageDraw
from pitop.processing.algorithms.faces import (
    FaceDetector,
    EmotionDetector
)
from signal import pause
from pitop.processing.core.vision_functions import import_opencv


cv2 = import_opencv()

'''
Designed for the Prax robot configuration, this example will use the camera module to detect face emotions.
The emotion will be displayed on the miniscreen alongside a confidence level. Also displayed is a live 68-point facial
landmark detection of the face being detected.

To change emoji's, go here to see a list of unicodes: https://unicode.org/emoji/charts/full-emoji-list.html
'''

emoji_unicodes = {
    "Happy": u"\U0001F642",
    "Anger": u"\U0001F620",
    "Surprise": u"\U0001F62E",
    "Neutral": u"\U0001F610",
    "Sad": u"\U0001F641",
    "Disgust": u"\U0001F62C",
    "Looking": u"\U0001F440"
}


text_font = ImageFont.truetype("VeraMono.ttf", size=12)
emoji_font = ImageFont.truetype("Symbola.ttf", size=50, encoding='unic')
looking_for_face_count = 0
contrast_reset = False
miniscreen_contrast = 255


def draw_top_text(canvas, text):
    w_t, h_t = text_font.getsize(text)
    confidence_text_pos = ((w_ms - w_t) // 2, 0)
    canvas.text(confidence_text_pos, text, fill=1, font=text_font)


def draw_emoji(canvas, emoji, bounding_box, offset_y=2):
    emoji_text = emoji_unicodes[emoji]
    w_e, h_e = emoji_font.getsize(emoji_text)
    x_b, y_b, w_b, h_b = bounding_box
    emoji_text_pos = (x_b + (w_b - w_e) // 2, y_b + (h_b - h_e) // 2 - offset_y)
    canvas.text(emoji_text_pos, emoji_text, fill=1, font=emoji_font)


def draw_emotion_data(canvas, emotion):
    confidence_text = f"{round(emotion.confidence * 100)}% {emotion.type}"
    draw_top_text(canvas, confidence_text)
    draw_emoji(canvas, emotion.type, right_bounding_box)


def draw_facial_landmarks(canvas, face):
    x_f, y_f, w_f, h_f = face.rectangle
    x_l, y_l, w_l, h_l = left_bounding_box

    translation_vector = [x_f - x_l + (w_l - w_f) // 2, y_f - y_l + (h_l - h_f) // 2]

    scaler_width = w_l / w_f
    scaler_height = h_l / h_f
    if scaler_width < scaler_height:
        scaler = scaler_width
    else:
        scaler = scaler_height

    scaler *= 0.8  # scale further by 0.8 as face rectangle often smaller than face feature bounds

    face_features = (face.features - translation_vector) * scaler

    for (x, y) in face_features:
        canvas.point((x, y), fill=1)


def found_face_display(canvas, face, emotion):
    global looking_for_face_count, miniscreen_contrast, contrast_reset
    looking_for_face_count = 0
    miniscreen_contrast = 255
    if not contrast_reset:
        robot.miniscreen.contrast(miniscreen_contrast)
        contrast_reset = True
    draw_facial_landmarks(canvas=canvas, face=face)
    draw_emotion_data(canvas=canvas, emotion=emotion)


def looking_for_face_display(canvas):
    global looking_for_face_count

    if looking_for_face_count > 100:
        global miniscreen_contrast, contrast_reset
        miniscreen_contrast = max(0, miniscreen_contrast - 1)
        robot.miniscreen.contrast(miniscreen_contrast)
        contrast_reset = False

    draw_emoji(canvas=canvas, emoji="Looking", bounding_box=wide_bounding_box, offset_y=5)

    text = "Looking..."
    draw_top_text(canvas=canvas, text=text)

    looking_for_face_count += 1


def frame_callback(frame):
    face = face_detector.detect(frame)
    emotion = emotion_detector.detect(face)

    canvas = ImageDraw.Draw(image)
    canvas.rectangle(robot.miniscreen.bounding_box, fill=0)

    if face.found:
        found_face_display(canvas, face, emotion)
    else:
        looking_for_face_display(canvas)

    robot.miniscreen.display_image(image)


robot = Pitop()
camera = Camera(flip_top_bottom=True)
robot.add_component(camera)

image = Image.new(
    robot.miniscreen.mode,
    robot.miniscreen.size,
)

w_ms, h_ms = robot.miniscreen.size

sample_text = "100% Happy"
_, top_section_height = text_font.getsize(sample_text)

left_bounding_box = (0, top_section_height, w_ms // 2, h_ms - top_section_height)
right_bounding_box = (w_ms // 2, top_section_height, w_ms // 2, h_ms - top_section_height)
wide_bounding_box = (0, top_section_height, w_ms, h_ms - top_section_height)

face_detector = FaceDetector()
emotion_detector = EmotionDetector(input_format="OpenCV", format="OpenCV")

robot.camera.on_frame = frame_callback

pause()
