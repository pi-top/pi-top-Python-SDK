from pitop import Camera, Pitop

camera = Camera()
pitop = Pitop()
camera.on_frame = pitop.miniscreen.display_image
