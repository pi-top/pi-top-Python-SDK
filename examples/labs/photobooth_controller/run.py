from pitop.labs import WebController

from pitop import Camera, Pitop

photobooth = Pitop()
photobooth.add_component(Camera())


def save_photo(data):
    photobooth.camera.current_frame().save(f'{data["name"]}.jpg')


controller = WebController(
    get_frame=photobooth.camera.get_frame, message_handlers={"save_photo": save_photo}
)

controller.serve_forever()
