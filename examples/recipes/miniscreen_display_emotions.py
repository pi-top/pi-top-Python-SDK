from signal import pause

from PIL import Image, ImageDraw, ImageFont
from pitop import Camera, Pitop
from pitop.processing.algorithms.faces import EmotionClassifier, FaceDetector

"""
Designed for the Prax robot configuration, this example will use the camera module to detect face emotions.
The emotion will be displayed on the miniscreen alongside a confidence level. Also displayed is a live 68-point facial
landmark detection of the face being detected.

To change emoji's, go here to see a list of unicodes: https://unicode.org/emoji/charts/full-emoji-list.html
"""

emoji_unicodes = {
    "Happy": "\U0001F642",
    "Anger": "\U0001F620",
    "Surprise": "\U0001F62E",
    "Neutral": "\U0001F610",
    "Sad": "\U0001F641",
    "Disgust": "\U0001F62C",
    "Looking": "\U0001F440",
}


text_font = ImageFont.truetype("VeraMono.ttf", size=12)
emoji_font = ImageFont.truetype("Symbola_hint.ttf", size=50, encoding="unic")


def update_displayed_image(face, emotion):
    def draw_text(canvas, text):
        w_t, h_t = text_font.getsize(text)
        confidence_text_pos = ((w_ms - w_t) // 2, 0)
        canvas.text(confidence_text_pos, text, fill=1, font=text_font)

    def draw_emoji(canvas, emoji, bounding_box, offset_y=2):
        emoji_text = emoji_unicodes[emoji]
        w_e, h_e = emoji_font.getsize(emoji_text)
        x_b, y_b, w_b, h_b = bounding_box
        emoji_text_pos = (x_b + (w_b - w_e) // 2, y_b + (h_b - h_e) // 2 - offset_y)
        canvas.text(emoji_text_pos, emoji_text, fill=1, font=emoji_font)

    def draw_facial_landmarks(canvas, face):
        x_f, y_f, w_f, h_f = face.rectangle
        x_l, y_l, w_l, h_l = left_bounding_box
        translation_vector = [
            x_f - x_l + (w_l - w_f) // 2,
            y_f - y_l + (h_l - h_f) // 2,
        ]

        scaler_width = w_l / w_f
        scaler_height = h_l / h_f
        scaler = scaler_width if scaler_width < scaler_height else scaler_height
        scaler *= 0.8  # scale further as face rectangle is often smaller than face feature bounds
        face_features = (face.features - translation_vector) * scaler

        for (x, y) in face_features:
            canvas.point((x, y), fill=1)

    canvas = ImageDraw.Draw(image)
    canvas.rectangle(robot.miniscreen.bounding_box, fill=0)

    if face.found:
        draw_facial_landmarks(canvas=canvas, face=face)
        draw_emoji(canvas, emotion.type, right_bounding_box)
        draw_text(canvas, f"{round(emotion.confidence * 100)}% {emotion.type}")
    else:
        draw_emoji(
            canvas=canvas, emoji="Looking", bounding_box=wide_bounding_box, offset_y=5
        )
        draw_text(canvas=canvas, text="Looking...")

    robot.miniscreen.display_image(image)


def run_emotion_and_face_detector(frame):
    face = face_detector(frame)
    emotion = emotion_classifier(face)
    update_displayed_image(face, emotion)


robot = Pitop()
camera = Camera(resolution=(640, 480), flip_top_bottom=True)
robot.add_component(camera)

image = Image.new(
    robot.miniscreen.mode,
    robot.miniscreen.size,
)

w_ms, h_ms = robot.miniscreen.size

sample_text = "100% Happy"
_, top_section_height = text_font.getsize(sample_text)

left_bounding_box = (0, top_section_height, w_ms // 2, h_ms - top_section_height)
right_bounding_box = (
    w_ms // 2,
    top_section_height,
    w_ms // 2,
    h_ms - top_section_height,
)
wide_bounding_box = (0, top_section_height, w_ms, h_ms - top_section_height)

face_detector = FaceDetector()
emotion_classifier = EmotionClassifier()

robot.camera.on_frame = run_emotion_and_face_detector

pause()
