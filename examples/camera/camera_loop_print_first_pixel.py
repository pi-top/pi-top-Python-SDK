from pitop import Camera

cam = Camera()

while True:
    image = cam.get_frame()
    print(image.getpixel((0, 0)))
