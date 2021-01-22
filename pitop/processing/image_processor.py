from pitop.processing.algorithms import find_line


class ImageProcessor:
    line_detect = find_line

    def __init__(self):
        self.on_frame = None
        self.transforms = list()

    def add_transform(self, transform_function):
        self.transforms.append(transform_function)
        return self

    def process(self, frame):
        for transform_fcn in self.transforms:
            result, frame = transform_fcn(frame)

        if callable(self.on_frame):
            self.on_frame((frame, result))
