from pitop.camera import Camera
from pitop.miniscreen import Miniscreen


camera = Camera()
miniscreen = Miniscreen()
camera.on_frame = miniscreen.display_image
