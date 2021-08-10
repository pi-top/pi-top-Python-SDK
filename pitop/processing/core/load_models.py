from os import path
from pathlib import Path


def retrieve_model(model_filename, base_download_link):
    def download_file(url, output_file_path):
        import wget
        import sys
        print("Downloading model file...")
        bar = wget.bar_adaptive if hasattr(sys.stdout, "fileno") else None
        try:
            wget.download(url, output_file_path, bar=bar)
        except Exception as e:
            print(e)
            raise RuntimeError("Downloading model failed, please check the model_filename is correct. If issue "
                               "persists, please report it here: https://github.com/pi-top/pi-top-Python-SDK/issues")
        print()
        print("Download complete!")

    def extract_file(compressed_file_path, output_file_path):
        import bz2
        print("Extracting model file...")
        with open(compressed_file_path, 'rb') as source, open(output_file_path, 'wb') as dest:
            dest.write(bz2.decompress(source.read()))
        print("Extraction complete!")

    model_dir = path.join(".config", "pi-top", "sdk", "models")
    abs_model_dir = path.join(str(Path.home()), model_dir)
    model_file_path = path.join(abs_model_dir, model_filename)

    if path.exists(model_file_path):
        return model_file_path

    print(f"Required model file (\"{model_filename}\") not found.")

    Path(abs_model_dir).mkdir(parents=True, exist_ok=True)

    compressed_model_filename = f"{model_filename}.bz2"
    download_file_path = path.join(abs_model_dir, compressed_model_filename)

    download_file(url=f"{base_download_link}{compressed_model_filename}", output_file_path=download_file_path)
    extract_file(compressed_file_path=download_file_path, output_file_path=model_file_path)

    return model_file_path


def load_emotion_model(model_filename="emotion_classification_model_svc_v1.onnx"):
    try:
        import onnxruntime as rt
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "onnxruntime Python library is not installed. You can install it by running 'sudo apt install python3-onnxruntime'.") from None

    model_file_path = retrieve_model(model_filename=model_filename,
                                     base_download_link="https://github.com/pi-top/Machine-Learning-Models/raw/master/")

    if path.exists(model_file_path):
        return rt.InferenceSession(model_file_path)
    else:
        raise RuntimeError("Retrieving model failed, please try again. If issue persists, please report it here: "
                           "https://github.com/pi-top/pi-top-Python-SDK/issues")


def load_face_landmark_predictor(model_filename):
    from pitop.processing.core.vision_functions import import_dlib

    dlib = import_dlib()

    model_file_path = retrieve_model(model_filename=model_filename,
                                     base_download_link="https://github.com/davisking/dlib-models/raw/master/")

    if path.exists(model_file_path):
        return dlib.shape_predictor(model_file_path)
    else:
        raise RuntimeError("Retrieving model failed, please try again. If issue persists, please report it here: "
                           "https://github.com/pi-top/pi-top-Python-SDK/issues")
