# Example code using particles to make a hyperspace-like screensaver

from pitop.miniscreen import OLED
from random import randint

oled_display = OLED()
canvas = oled_display.canvas

screen_width = canvas.get_width()
screen_height = canvas.get_height()
speed_factor = 15
particle_count = 15
particles = []


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def get_position(self):
        return (self.x, self.y)

    def update(self):
        dx = (self.x - (screen_width / 2)) / speed_factor if self.x < (screen_width /
                                                                       2) else (self.x - (screen_width / 2)) / speed_factor
        dy = (self.y - (screen_height / 2)) / speed_factor if self.y < (screen_height /
                                                                        2) else (self.y - (screen_height / 2)) / speed_factor
        self.x += dx
        self.y += dy


def add_new_particle():
    x = randint(0, screen_width)
    y = randint(0, screen_height)
    particles.append(Particle(x, y))


while True:
    canvas.clear()
    particles.clear()

    speed_factor = randint(5, 30)
    particle_count = randint(5, 50)

    for count in range(particle_count):
        add_new_particle()

    for _ in range(100):
        for particle in particles:
            x, y = particle.get_position()

            if (x < 0 or x > screen_width) or (y < 0 or y > screen_height):
                particles.remove(particle)
                add_new_particle()
            else:
                canvas.point((x, y))
                particle.update()

        oled_display.draw()
