from random import randint, random
from time import sleep

from PIL import Image, ImageDraw
from pitop import Pitop

# https://en.wikipedia.org/wiki/Maze_generation_algorithm

pitop = Pitop()
miniscreen = pitop.miniscreen
image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)
canvas = ImageDraw.Draw(image)
miniscreen.set_max_fps(50)


def draw_pixel(pos):
    canvas.point(pos, fill=1)
    miniscreen.display_image(image)
    drawn_pixels.append(pos)


width = (miniscreen.width // 2) * 2 - 1
height = (miniscreen.height // 2) * 2 - 1

while True:

    print("Initialising...")
    canvas.rectangle(miniscreen.bounding_box, fill=0)

    drawn_pixels = list()
    complexity = int(random() * (5 * (width + height)))
    density = int(random() * ((width // 2) * (height // 2)))

    print("Drawing the borders...")

    for x in range(width):
        draw_pixel((x, 0))
        draw_pixel((x, (height // 2) * 2))

    for y in range(height):
        draw_pixel((0, y))
        draw_pixel(((width // 2) * 2, y))

    print("Filling the maze...")

    for i in range(density):
        x, y = randint(0, width // 2) * 2, randint(0, height // 2) * 2
        if (x, y) not in drawn_pixels:
            draw_pixel((x, y))

            for j in range(complexity):
                neighbours = []
                if x > 1:
                    neighbours.append((x - 2, y))
                if x < width - 3:
                    neighbours.append((x + 2, y))
                if y > 1:
                    neighbours.append((x, y - 2))
                if y < height - 3:
                    neighbours.append((x, y + 2))
                if len(neighbours):
                    x_, y_ = neighbours[randint(0, len(neighbours) - 1)]
                    if (x_, y_) not in drawn_pixels:
                        draw_pixel((x_, y_))
                        draw_pixel((x_ + (x - x_) // 2, y_ + (y - y_) // 2))
                        x, y = x_, y_

    print("Done!")

    sleep(10)
