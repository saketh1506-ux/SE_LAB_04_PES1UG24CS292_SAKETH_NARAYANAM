import pygame

class Bullet:
    def __init__(self, x, y, width=4, height=12, speed=8, direction=-1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = direction  # -1 = moving up (player bullet), 1 = moving down (enemy bullet)

    def move(self):
        self.y += self.speed * self.direction

    def off_screen(self, screen_height):
        return self.y < 0 or self.y > screen_height

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
