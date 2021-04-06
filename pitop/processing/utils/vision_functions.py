
try:
    import cv2
except (ImportError, ModuleNotFoundError):
    raise ModuleNotFoundError(
        "OpenCV Python library is not installed. You can install it by running "
        "'sudo apt install python3-opencv libatlas-base-dev'.") from None


def import_opencv():
    try:
        import cv2
        return cv2
    except (ImportError, ModuleNotFoundError):
        raise ModuleNotFoundError(
            "OpenCV Python library is not installed. You can install it by running 'sudo apt install python3-opencv libatlas-base-dev'.") from None


def colour_mask(frame, hsv_lower, hsv_upper):
    # apply gaussian blur to smooth out the frame
    blur = cv2.blur(frame, (9, 9))

    # Convert BGR to HSV
    hsv_frame = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv_frame, hsv_lower, hsv_upper)

    return mask


def find_largest_contour(frame):
    # Find the contours of the frame. RETR_EXTERNAL: retrieves only the extreme outer contours
    image, contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the biggest contour (if detected)
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
    else:
        # no contours found, set to None
        largest_contour = None

    return largest_contour


def find_centroid(contour):
    if contour is not None:
        moments = cv2.moments(contour)
        # add 1e-5 to avoid division by zero (standard docs.opencv.org practice apparently)
        centroid_x = int(moments['m10'] / (moments['m00'] + 1e-5))
        centroid_y = int(moments['m01'] / (moments['m00'] + 1e-5))
    else:
        # no centroid found, set to none and deal with this case as necessary
        centroid_x = None
        centroid_y = None

    return centroid_x, centroid_y


def find_largest_rectangle(rectangles):
    area = 0
    current_index = 0
    largest_index = 0
    for x, y, w, h in rectangles:
        current_area = w * h
        if current_area > area:
            area = current_area
            largest_index = current_index
        current_index += 1

    return rectangles[largest_index]


def scale_frame(frame, scale):
    scaled_width = int(frame.shape[1] * scale)
    scaled_height = int(frame.shape[0] * scale)
    dim = (scaled_width, scaled_height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def center_reposition(center, frame):
    """Reposition center so that (0, 0) is in the middle of the frame instead
    of OpenCV standard which is at top left.

    :param center: OpenCV center (x, y)
    :param frame: Frame to reposition center within
    :return:
    """
    if center is None:
        return None
    # convert so (0, 0) is at the middle bottom of the frame
    center_x = center[0] - int(frame.shape[1] / 2)
    center_y = int(frame.shape[0] / 2) - center[1]

    return center_x, center_y
