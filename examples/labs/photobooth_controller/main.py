from pitop import Camera
from pitop.labs import WebController

camera = Camera()


def save_photo(data):
    camera.current_frame().save(f'{data.name}.jpg')


controller = WebController(handlers={'save_photo': save_photo})

controller.serve_forever()
