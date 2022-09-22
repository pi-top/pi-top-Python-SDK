import pygame
from signal import pause
from time import sleep

width = 780;
height = 620;
size = width, height

pitop_size = 250, 250
pitop_pos = (width / 2), (height / 2)

led_size = 50, 50
led_pos = pitop_pos[0] + 200, pitop_pos[1] - 50


class Pitop(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Pitop.png")
        self.rect = self.image.get_rect()
        self.rect.x = pitop_pos[0]
        self.rect.y = pitop_pos[1]

led_on = False

class LED(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("LED_green_off.png")
        self.rect = self.image.get_rect()
        self.rect.x = led_pos[0]
        self.rect.y = led_pos[1]

    def update(self):
      if led_on:
          self.image = pygame.image.load("LED_green_on.png")
      else:
          self.image = pygame.image.load("LED_green_off.png")

class Button(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Button.png")
        self.rect = self.image.get_rect()
        self.rect.x = led_pos[0]
        self.rect.y = led_pos[1] + 50





running = True
def main():
    global running

    pygame.init()
    screen = pygame.display.set_mode([width, height])

    screen.fill((0, 0, 255))

    p = Pitop()
    l = LED()
    b = Button()

    s = pygame.sprite.Group()
    s.add(p)
    s.add(l)
    s.add(b)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if b.rect.x <= mouse[0] <= b.rect.x + b.rect.width and b.rect.y <= mouse[1] <= b.rect.y + b.rect.height:
                    led_on = True

            if event.type == pygame.MOUSEBUTTONUP:
                    led_on = False



        s.update()
        s.draw(screen)
        pygame.display.flip()

from threading import Thread
t = Thread(target=main, daemon=True)

print('runnung  sim', flush=True)
t.start()
print('sleeping 10')
sleep(10)
print('quitting pygame')
running = False
sleep(1)
pygame.quit()
print('done')
