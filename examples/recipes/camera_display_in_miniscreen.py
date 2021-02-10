from pitop import Camera, Miniscreen


camera = Camera()
miniscreen = Miniscreen()
camera.on_frame = miniscreen.display_image
