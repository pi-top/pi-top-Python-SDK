import random
# import pygame
# import sys
# from pygame.locals import *

from pitop.miniscreen import Miniscreen
from PIL import Image, ImageDraw

from time import sleep

# pygame.init()
# fps = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# globals
WIDTH = 128
HEIGHT = 64
BALL_RADIUS = 4
PAD_WIDTH = 4
PAD_HEIGHT = 20
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
ball_pos = [0, 0]
ball_vel = [0, 0]
paddle1_vel = 0
paddle2_vel = 0
PADDLE_CONTROL_VELOCITY = 4
l_score = 0
r_score = 0

# canvas declaration
miniscreen = Miniscreen()
image = Image.new(
    miniscreen.mode,
    miniscreen.size,
)
canvas = ImageDraw.Draw(image)
miniscreen.set_max_fps(30)
bounding_box = miniscreen.bounding_box


# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
def ball_init(right):
    global ball_pos, ball_vel  # these are vectors stored as lists
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(2, 4)
    vert = random.randrange(1, 3)

    if right == False:
        horz = - horz

    ball_vel = [horz, -vert]


# define event handlers
def init():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    paddle1_pos = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2_pos = [WIDTH - 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


def get_circle_bounds(center, radius):
    x0 = center[0] - radius
    y0 = center[1] - radius
    x1 = center[0] + radius
    y1 = center[1] + radius
    # top_left = (center[0] - radius, center[1] + radius)
    # bottom_right = (center[0] + radius, center[1] - radius)
    # print([top_left, bottom_right])
    bound = (x0, y0, x1, y1)
    return bound


# draw function of canvas
def draw():
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score

    canvas.rectangle(bounding_box, fill=0)

    if HALF_PAD_HEIGHT < paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        print("pad is in the middle")
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] < HALF_PAD_HEIGHT and paddle1_vel > 0:
        print("pad is at the top")
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] > HEIGHT - HALF_PAD_HEIGHT and paddle1_vel < 0:
        print("pad is at the bottom")
        paddle1_pos[1] += paddle1_vel

    if HALF_PAD_HEIGHT < paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        print("pad is in the middle")
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] < HALF_PAD_HEIGHT and paddle2_vel > 0:
        print("pad is at the top")
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] > HEIGHT - HALF_PAD_HEIGHT and paddle2_vel < 0:
        print("pad is at the bottom")
        paddle2_pos[1] += paddle2_vel

    # update ball
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    # draw paddles and ball
    # canvas.ellipse((32, 0, 95, 63), fill=1)
    canvas.ellipse(get_circle_bounds(ball_pos, BALL_RADIUS), fill=1)
    # canvas.ellipse((28, 24, 48, 4), fill=1)

    canvas.line([(paddle1_pos[0], paddle1_pos[1] - HALF_PAD_HEIGHT),
                 (paddle1_pos[0], paddle1_pos[1] + HALF_PAD_HEIGHT)],
                fill=1,
                width=PAD_WIDTH)

    print(paddle2_pos)
    canvas.line([(paddle2_pos[0], paddle2_pos[1] - HALF_PAD_HEIGHT),
                 (paddle2_pos[0], paddle2_pos[1] + HALF_PAD_HEIGHT)],
                fill=1,
                width=PAD_WIDTH)

    # ball collision check on top and bottom walls
    if int(ball_pos[1]) <= BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]
    if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # ball collison check on gutters or paddles
    if int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - HALF_PAD_HEIGHT,
                                                                                 paddle1_pos[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH:
        r_score += 1
        ball_init(True)

    if int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[1]) in range(
            paddle2_pos[1] - HALF_PAD_HEIGHT, paddle2_pos[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
        l_score += 1
        ball_init(False)

    miniscreen.display_image(image)
    # update scores
    # myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    # label1 = myfont1.render("Score " + str(l_score), 1, (255, 255, 0))
    # canvas.blit(label1, (50, 20))
    #
    # myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
    # label2 = myfont2.render("Score " + str(r_score), 1, (255, 255, 0))
    # canvas.blit(label2, (470, 20))


def paddle_2_down_action():
    global paddle2_vel
    print("DOWN")
    paddle2_vel = PADDLE_CONTROL_VELOCITY


def paddle_2_up_action():
    global paddle2_vel
    print("UP")
    paddle2_vel = -PADDLE_CONTROL_VELOCITY


def paddle_2_stop():
    global paddle2_vel
    paddle2_vel = 0


def paddle_1_down_action():
    global paddle1_vel
    paddle1_vel = PADDLE_CONTROL_VELOCITY


def paddle_1_up_action():
    global paddle1_vel
    paddle1_vel = -PADDLE_CONTROL_VELOCITY

def paddle_1_stop():
    global paddle1_vel
    paddle1_vel = 0


init()

# miniscreen.select_button.when_pressed = paddle_2_down_action
# miniscreen.select_button.when_released = paddle_2_stop
#
# miniscreen.cancel_button.when_pressed = paddle_2_up_action
# miniscreen.cancel_button.when_released = paddle_2_stop

import threading



def check_key_states():
    pass

key_state = threading.Thread(target=check_key_states)
key_state.start()

paddle_1_key_states = [0, 0]
paddle_2_key_states = [0, 0]
# game loop
while True:
    draw()

    if miniscreen.select_button.is_pressed:
        paddle_2_key_states[0] = 1
    else:
        paddle_2_key_states[0] = 0

    if miniscreen.cancel_button.is_pressed:
        paddle_2_key_states[1] = 1
    else:
        paddle_2_key_states[1] = 0

    if paddle_2_key_states[0] == 1 and paddle_2_key_states[1] == 1:
        paddle_2_stop()
    elif paddle_2_key_states[0] == 0 and paddle_2_key_states[1] == 0:
        paddle_2_stop()
    elif paddle_2_key_states[0] == 1:
        paddle_2_down_action()
    elif paddle_2_key_states[1] == 1:
        paddle_2_up_action()

    if miniscreen.down_button.is_pressed:
        paddle_1_key_states[0] = 1
    else:
        paddle_1_key_states[0] = 0

    if miniscreen.up_button.is_pressed:
        paddle_1_key_states[1] = 1
    else:
        paddle_1_key_states[1] = 0

    if paddle_1_key_states[0] == 1 and paddle_1_key_states[1] == 1:
        paddle_1_stop()
    elif paddle_1_key_states[0] == 0 and paddle_1_key_states[1] == 0:
        paddle_1_stop()
    elif paddle_1_key_states[0] == 1:
        paddle_1_down_action()
    elif paddle_1_key_states[1] == 1:
        paddle_1_up_action()
