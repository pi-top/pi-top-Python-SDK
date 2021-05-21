def get_face_angle(face_features):
    """Returns angle in degrees of face from dlib face features.

    :param face_features: dlib face features (either 5 landmark or 68 landmark version)
    :return: angle of face in degrees
    """
    from imutils import face_utils
    import numpy as np
    import math

    if len(face_features) == 68:
        # https://pyimagesearch.com/wp-content/uploads/2017/04/facial_landmarks_68markup.jpg
        # note: array is 0-indexed, image annotations are 1-indexed

        left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
        right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
        left_eyebrow_start, left_eyebrow_end = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eyebrow"]
        right_eyebrow_start, right_eyebrow_end = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eyebrow"]
        jaw_start, jaw_end = face_utils.FACIAL_LANDMARKS_68_IDXS["jaw"]

        left_eye = face_features[left_eye_start:left_eye_end]
        right_eye = face_features[right_eye_start:right_eye_end]

        left_eyebrow = face_features[left_eyebrow_start: left_eyebrow_end]
        right_eyebrow = face_features[right_eyebrow_start: right_eyebrow_end]

        left_jaw = face_features[(jaw_end + 1) // 2:jaw_end]
        right_jaw = face_features[jaw_start:(jaw_end - 1) // 2]

        left_mouth = np.take(face_features, (52, 53, 54, 55, 56, 63, 64, 65), axis=0)
        right_mouth = np.take(face_features, (48, 49, 50, 58, 59, 60, 61, 67), axis=0)

        all_left_points = np.vstack((left_eye, left_eyebrow, left_jaw, left_mouth))
        all_right_points = np.vstack((right_eye, right_eyebrow, right_jaw, right_mouth))

    elif len(face_features) == 5:
        left_eye_start, left_eye_end = face_utils.FACIAL_LANDMARKS_5_IDXS["left_eye"]
        right_eye_start, right_eye_end = face_utils.FACIAL_LANDMARKS_5_IDXS["right_eye"]
        all_left_points = face_features[left_eye_start:left_eye_end]
        all_right_points = face_features[right_eye_start:right_eye_end]

    else:
        raise ValueError("dlib face features not recognised, please try again")

    left_centroid = np.average(all_left_points, axis=0)
    right_centroid = np.average(all_right_points, axis=0)

    position_diff = left_centroid - right_centroid

    x_diff, y_diff = position_diff

    angle = -math.degrees(math.atan(y_diff/x_diff))

    return round(angle, 1)


def load_emotion_model():
    import onnxruntime as rt
    from os import path

    model_dir = 'models'
    script_dir = path.dirname(path.realpath(__file__))
    abs_file_path = path.join(script_dir, model_dir)
    onnx_model_filename = "emotion_classification_model_svc_v1.onnx"

    return rt.InferenceSession(path.join(abs_file_path, onnx_model_filename))


def load_face_landmark_predictor(filename):
    from pitop.processing.core.vision_functions import import_dlib
    from sys import exit
    from pathlib import Path
    from os import path
    dlib = import_dlib()

    def busy_animation(subprocess_object):
        from time import sleep
        animation = "|/-\\"
        idx = 0
        while subprocess_object.poll() is None:
            print(animation[idx % len(animation)], end="\r")
            idx += 1
            sleep(0.1)

    def check_error(subprocess_object):
        import subprocess
        if subprocess_object.returncode != 0:
            if path.exists(path.join(abs_dlib_model_dir, compressed_model_filename)):
                # delete downloaded file as it is likely corrupt
                subprocess.run(["rm", "compressed_model_filename"], cwd=abs_dlib_model_dir)

            print("Retrieving model failed, please try again. If issue persists, please report it here: "
                  "https://github.com/pi-top/pi-top-Python-SDK/issues")
            exit()

    def download():
        import subprocess
        print("Downloading model file...")

        download_link = f"https://github.com/davisking/dlib-models/raw/master/{compressed_model_filename}"
        download_file = subprocess.Popen(["wget", "-P", abs_dlib_model_dir, download_link],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL
                                         )
        busy_animation(subprocess_object=download_file)
        check_error(subprocess_object=download_file)

        print("Download complete!")

    def decompress():
        import subprocess
        print("Decompressing model file...")
        decompress_file = subprocess.Popen(["bzip2", "-d", f"{compressed_model_filename}"],
                                           cwd=abs_dlib_model_dir,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL
                                           )
        busy_animation(subprocess_object=decompress_file)
        check_error(subprocess_object=decompress_file)

        print("Decompression Complete! Returning back to your program now...")
        return dlib.shape_predictor(dlib_model_file_path)

    dlib_model_dir = path.join(".config", "pi-top", "sdk", "dlib_models")
    abs_dlib_model_dir = path.join(str(Path.home()), dlib_model_dir)
    dlib_model_file_path = path.join(abs_dlib_model_dir, filename)

    if path.exists(dlib_model_file_path):
        return dlib.shape_predictor(dlib_model_file_path)

    print("Required model file not found.")

    Path(abs_dlib_model_dir).mkdir(parents=True, exist_ok=True)

    compressed_model_filename = f"{filename}.bz2"
    if path.exists(path.join(abs_dlib_model_dir, compressed_model_filename)):
        # File has already been downloaded
        return decompress()

    download()
    return decompress()
