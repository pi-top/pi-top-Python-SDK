from pitop.processing.algorithms import find_line


class ImageProcessor:
    line_detect = find_line

    def __init__(self, frame_source):
        self.on_new_frame = None
        self.__process = frame_source
        self.transforms = list()

    def add_transform(self, transform_function):
        self.transforms.append(transform_function)

    def __process(self, frame):
        for transform_fcn in self.transforms:
            result, frame = transform_fcn(frame)

        if callable(self.on_new_frame):
            self.on_new_frame((frame, result))
