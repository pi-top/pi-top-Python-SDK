from pitop.camera import Camera

cam = Camera()

while True:
    image = cam.get_frame()
    image.show()
