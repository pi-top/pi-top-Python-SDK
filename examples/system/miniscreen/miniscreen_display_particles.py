from random import randint

from PIL import Image, ImageDraw
from pitop import Pitop

pitop = Pitop()
miniscreen = pitop.miniscreen
image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)
canvas = ImageDraw.Draw(image)

speed_factor = 15
particles = []


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def get_position(self):
        return (self.x, self.y)

    def update(self):
        dx = (
            (self.x - (miniscreen.width / 2)) / speed_factor
            if self.x < (miniscreen.width / 2)
            else (self.x - (miniscreen.width / 2)) / speed_factor
        )
        dy = (
            (self.y - (miniscreen.height / 2)) / speed_factor
            if self.y < (miniscreen.height / 2)
            else (self.y - (miniscreen.height / 2)) / speed_factor
        )
        self.x += dx
        self.y += dy


def add_new_particle():
    x = randint(0, miniscreen.width)
    y = randint(0, miniscreen.height)
    particles.append(Particle(x, y))


while True:
    # Clear display
    canvas.rectangle(miniscreen.bounding_box, fill=0)
    particles.clear()

    speed_factor = randint(5, 30)
    particle_count = randint(5, 50)

    for count in range(particle_count):
        add_new_particle()

    for _ in range(100):
        for particle in particles:
            x, y = particle.get_position()

            if (x < 0 or x > miniscreen.width) or (y < 0 or y > miniscreen.height):
                particles.remove(particle)
                add_new_particle()
            else:
                canvas.point((x, y), fill=1)
                particle.update()

        miniscreen.display_image(image)
