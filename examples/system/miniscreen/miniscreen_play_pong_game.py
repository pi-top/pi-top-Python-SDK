from random import randrange
from time import sleep

from PIL import Image, ImageDraw, ImageFont
from pitop import Pitop

# Game variables
BALL_RADIUS = 2
PADDLE_SIZE = (2, 20)
PADDLE_CTRL_VEL = 4


class Ball:
    def __init__(self):
        self.pos = [0, 0]
        self.vel = [0, 0]

        # 50/50 chance of direction
        self.init(move_right=randrange(0, 2) == 0)

    def init(self, move_right):
        self.pos = [miniscreen.width // 2, miniscreen.height // 2]

        horz = randrange(1, 3)
        vert = randrange(1, 3)

        if move_right is False:
            horz = -horz

        self.vel = [horz, -vert]

    @property
    def x_pos(self):
        return self.pos[0]

    @property
    def y_pos(self):
        return self.pos[1]

    def is_aligned_with_paddle_horizontally(self, paddle):
        return abs(self.x_pos - paddle.x_pos) <= BALL_RADIUS + PADDLE_SIZE[0] // 2

    def is_aligned_with_paddle_vertically(self, paddle):
        return abs(self.y_pos - paddle.y_pos) <= BALL_RADIUS + PADDLE_SIZE[1] // 2

    def is_touching_paddle(self, paddle):
        hor = self.is_aligned_with_paddle_horizontally(paddle)
        ver = self.is_aligned_with_paddle_vertically(paddle)
        return hor and ver

    @property
    def is_touching_vertical_walls(self):
        return (
            self.y_pos <= BALL_RADIUS
            or self.y_pos >= miniscreen.height + 1 - BALL_RADIUS
        )

    def change_direction(self, change_x=False, change_y=False, speed_factor=1.0):
        x_vel = -self.vel[0] if change_x else self.vel[0]
        self.vel[0] = speed_factor * x_vel

        y_vel = -self.vel[1] if change_y else self.vel[1]
        self.vel[1] = speed_factor * y_vel

    def update(self):
        self.pos = [x + y for x, y in zip(self.pos, self.vel)]

        if self.is_touching_vertical_walls:
            self.change_direction(change_y=True, speed_factor=1.0)

    @property
    def bounding_box(self):
        def get_circle_bounds(center, radius):
            x0 = center[0] - radius
            y0 = center[1] - radius
            x1 = center[0] + radius
            y1 = center[1] + radius
            return (x0, y0, x1, y1)

        return get_circle_bounds(self.pos, BALL_RADIUS)


class Paddle:
    def __init__(self, start_pos=[0, 0]):
        self.pos = start_pos
        self.vel = 0
        self.score = 0

    def increase_score(self):
        self.score += 1

    @property
    def x_pos(self):
        return self.pos[0]

    @property
    def y_pos(self):
        return self.pos[1]

    @y_pos.setter
    def y_pos(self, new_y):
        self.pos[1] = new_y

    @property
    def touching_top(self):
        return self.y_pos - PADDLE_SIZE[1] // 2 <= 0

    @property
    def touching_bottom(self):
        return self.y_pos + PADDLE_SIZE[1] // 2 >= miniscreen.height - 1

    def update(self):
        moving_down = self.vel > 0

        if self.touching_top and not moving_down:
            return

        if self.touching_bottom and moving_down:
            return

        self.y_pos += self.vel

        if self.touching_top:
            self.y_pos = PADDLE_SIZE[1] // 2

        if self.touching_bottom:
            self.y_pos = miniscreen.height - PADDLE_SIZE[1] // 2 - 1

    @property
    def bounding_box(self):
        return (
            self.x_pos,
            self.y_pos - PADDLE_SIZE[1] // 2,
            self.x_pos,
            self.y_pos + PADDLE_SIZE[1] // 2,
        )


def update_button_state():
    down_pressed = miniscreen.down_button.is_pressed
    up_pressed = miniscreen.up_button.is_pressed
    select_pressed = miniscreen.select_button.is_pressed
    cancel_pressed = miniscreen.cancel_button.is_pressed

    if down_pressed == up_pressed:
        l_paddle.vel = 0
    elif down_pressed:
        l_paddle.vel = PADDLE_CTRL_VEL
    elif up_pressed:
        l_paddle.vel = -PADDLE_CTRL_VEL

    if select_pressed == cancel_pressed:
        r_paddle.vel = 0
    elif select_pressed:
        r_paddle.vel = PADDLE_CTRL_VEL
    elif cancel_pressed:
        r_paddle.vel = -PADDLE_CTRL_VEL


def update_positions():
    round_finished = False

    l_paddle.update()
    r_paddle.update()
    ball.update()

    paddles = {l_paddle, r_paddle}
    for paddle in paddles:
        if ball.is_aligned_with_paddle_horizontally(paddle):
            if ball.is_touching_paddle(paddle):
                ball.change_direction(change_x=True, speed_factor=1.1)
            else:
                other_paddle = paddles - {paddle}
                other_paddle = other_paddle.pop()
                other_paddle.increase_score()

                ball.init(move_right=other_paddle == r_paddle)
                paddle.y_pos = miniscreen.height // 2
                other_paddle.y_pos = miniscreen.height // 2

                round_finished = True

            break

    return round_finished


def draw(wait=False):
    canvas = ImageDraw.Draw(image)

    # Clear screen
    canvas.rectangle(miniscreen.bounding_box, fill=0)

    # Draw ball
    canvas.ellipse(ball.bounding_box, fill=1)

    # Draw paddles
    canvas.line(l_paddle.bounding_box, fill=1, width=PADDLE_SIZE[0])

    canvas.line(r_paddle.bounding_box, fill=1, width=PADDLE_SIZE[0])

    # Draw score
    font = ImageFont.truetype("VeraMono.ttf", size=12)
    canvas.multiline_text(
        (1 * miniscreen.width // 3, 2),
        str(l_paddle.score),
        fill=1,
        font=font,
        align="center",
    )
    canvas.multiline_text(
        (2 * miniscreen.width // 3, 2),
        str(r_paddle.score),
        fill=1,
        font=font,
        align="center",
    )

    # Display image
    miniscreen.display_image(image)

    if wait:
        sleep(1.5)


# Internal variables
pitop = Pitop()
miniscreen = pitop.miniscreen
miniscreen.set_max_fps(30)

ball = Ball()

l_paddle = Paddle([PADDLE_SIZE[0] // 2 - 1, miniscreen.height // 2])
r_paddle = Paddle([miniscreen.width - 1 - PADDLE_SIZE[0] // 2, miniscreen.height // 2])

image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)


def main():
    while True:
        update_button_state()
        draw(update_positions())


if __name__ == "__main__":
    main()
