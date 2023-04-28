from random import randint
from time import sleep

from pitop.pulse import ledmatrix


class PongGameState:
    NO_RESULT = 0
    LEFT_BAT_WIN = 1
    RIGHT_BAT_WIN = 2

    def __init__(self):
        self.reset()

    def reset(self):
        self.bat_left_y = 2
        self.bat_right_y = 2
        self.bat_left_size = 4
        self.bat_right_size = 4

        self.ball_x = randint(3, 4)
        self.ball_y = randint(3, 4)

        self.ball_dx = 1 if randint(0, 1) == 0 else -1
        self.ball_dy = 1 if randint(0, 1) == 0 else -1

    def __adjust_ball_y_velocity(self, change):
        if self.ball_dy >= -1 and (self.ball_dy <= 1):
            self.ball_dy += change

    def increase_difficulty_level(self):
        if self.bat_left_size > 1:
            self.bat_left_size -= 1

        if self.bat_right_size > 1:
            self.bat_right_size -= 1

    def move_ball(self):
        if self.ball_y + self.ball_dy >= 7 or self.ball_y + self.ball_dy < 0:
            self.ball_dy *= -1

        if self.ball_x + self.ball_dx >= 7:
            return self.LEFT_BAT_WIN

        elif self.ball_x + self.ball_dx < 0:
            return self.RIGHT_BAT_WIN

        elif self.ball_x + self.ball_dx == 0:
            if self.ball_y == self.bat_left_y:
                self.ball_dx *= -1
                self.__adjust_ball_y_velocity(1)
            elif self.ball_y == self.bat_left_y + self.bat_left_size:
                self.ball_dx *= -1
                self.__adjust_ball_y_velocity(-1)
            elif (
                self.ball_y >= self.bat_left_y
                and self.ball_y <= self.bat_left_y + self.bat_left_size
            ):
                self.ball_dx *= -1

        elif self.ball_x + self.ball_dx == 6:
            if self.ball_y == self.bat_right_y:
                self.ball_dx *= -1
                self.__adjust_ball_y_velocity(1)
            elif self.ball_y == self.bat_right_y + self.bat_right_size:
                self.ball_dx *= -1
                self.__adjust_ball_y_velocity(-1)
            elif (
                self.ball_y >= self.bat_right_y
                and self.ball_y <= self.bat_right_y + self.bat_right_size
            ):
                self.ball_dx *= -1

        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        return self.NO_RESULT

    def __move_left_bat(self, movement):
        if self.bat_left_y + movement >= 0 and (
            (self.bat_left_y + self.bat_left_size + movement) < 7
        ):
            self.bat_left_y += movement

    def __move_right_bat(self, movement):
        if self.bat_right_y + movement >= 0 and (
            (self.bat_right_y + self.bat_right_size + movement) < 7
        ):
            self.bat_right_y += movement

    def move_bats(self):
        if self.ball_dx < 0:
            if self.ball_y > self.bat_left_y + (self.bat_left_size / 2):
                self.__move_left_bat(1)
            elif self.ball_y < self.bat_left_y + (self.bat_left_size / 2):
                self.__move_left_bat(-1)
        elif self.ball_dx > 0:
            if self.ball_y > self.bat_right_y + (self.bat_right_size / 2):
                self.__move_right_bat(1)
            elif self.ball_y < self.bat_right_y + (self.bat_right_size / 2):
                self.__move_right_bat(-1)


def draw_bats():
    for y in range(7):
        ledmatrix.set_pixel(
            0, y, background_color[0], background_color[1], background_color[2]
        )
        ledmatrix.set_pixel(
            6, y, background_color[0], background_color[1], background_color[2]
        )

    for y in range(game_state.bat_left_size):
        ledmatrix.set_pixel(
            0,
            y + game_state.bat_left_y,
            left_bat_color[0],
            left_bat_color[1],
            left_bat_color[2],
        )

    for y in range(game_state.bat_right_size):
        ledmatrix.set_pixel(
            6,
            y + game_state.bat_right_y,
            right_bat_color[0],
            right_bat_color[1],
            right_bat_color[2],
        )


def draw_ball():
    ledmatrix.set_pixel(
        game_state.ball_x,
        game_state.ball_y,
        ball_color[0],
        ball_color[1],
        ball_color[2],
    )


def flash_screen(rgb_tuple):
    for i in range(5):
        ledmatrix.set_all(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        ledmatrix.show()
        sleep(0.2)
        ledmatrix.set_all(background_color[0], background_color[1], background_color[2])
        ledmatrix.show()
        sleep(0.2)


game_state = PongGameState()
background_color = (0, 100, 0)
left_bat_color = (255, 0, 0)
right_bat_color = (0, 0, 255)
ball_color = (200, 200, 200)

turn_counter = 0

while True:
    ledmatrix.set_all(background_color[0], background_color[1], background_color[2])

    turn_counter += 1

    if turn_counter % 30 == 0:
        game_state.increase_difficulty_level()

    if turn_counter > 150:
        flash_screen(ball_color)
        turn_counter = 0
        game_state.reset()

    else:
        game_state.move_bats()
        result = game_state.move_ball()

        if result == game_state.LEFT_BAT_WIN:
            flash_screen(left_bat_color)
            turn_counter = 0
            game_state.reset()

        elif result == game_state.RIGHT_BAT_WIN:
            flash_screen(right_bat_color)
            turn_counter = 0
            game_state.reset()

        else:
            draw_ball()
            draw_bats()
            ledmatrix.show()

            sleep(0.05)
