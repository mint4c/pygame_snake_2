"""
sprites.py
sprite classes
"""

import pygame
import constants as c
import random


class Player(pygame.sprite.Sprite):
    # snake
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(
            c.snake_head_img,
            (
                c.SIZE_OF_SBLOCK,
                c.SIZE_OF_SBLOCK
            )
        )

        self.rect = self.image.get_rect()

        self.rect.center = (
            c.WIDTH / 2,
            c.HEIGHT / 2
        )

        self.speedx = 0
        self.speedy = 0

        self.posList = []

        self.length = 1
        self.score = 0
        self.direction = None

    @property
    def direction_name(self):
        direction_names = {
            "L": "left",
            "R": "right",
            "U": "up",
            "D": "down",
        }

        return direction_names.get(
            self.direction
        )

    def set_direction(self, action):
        if action == "left":
            self.speedx = -c.SPEED
            self.speedy = 0

            self.image = pygame.transform.rotate(
                c.snake_head_img,
                90
            )

            self.direction = "L"

        elif action == "right":
            self.speedx = c.SPEED
            self.speedy = 0

            self.image = pygame.transform.rotate(
                c.snake_head_img,
                270
            )

            self.direction = "R"

        elif action == "up":
            self.speedy = -c.SPEED
            self.speedx = 0

            self.image = pygame.transform.rotate(
                c.snake_head_img,
                360
            )

            self.direction = "U"

        elif action == "down":
            self.speedy = c.SPEED
            self.speedx = 0

            self.image = pygame.transform.rotate(
                c.snake_head_img,
                180
            )

            self.direction = "D"

    def would_collide(self, action):
        movement = {
            "left": (-c.SPEED, 0),
            "right": (c.SPEED, 0),
            "up": (0, -c.SPEED),
            "down": (0, c.SPEED),
        }

        dx, dy = movement[action]

        next_rect = self.rect.move(
            dx,
            dy
        )

        touches_wall = (
            next_rect.right >= c.WIDTH
            or next_rect.left < 0
            or next_rect.top < 0
            or next_rect.bottom >= c.HEIGHT
        )

        next_head = [
            next_rect.x,
            next_rect.y
        ]

        touches_body = (
            next_head in self.posList[:-1]
        )

        return touches_wall or touches_body

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def collision(self):
        self.length += 5
        self.score += 1


class Food(pygame.sprite.Sprite):
    # squares that the snake eats to get bigger
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(
            c.apple_img,
            (
                c.SIZE_OF_SBLOCK + 8,
                c.SIZE_OF_SBLOCK + 8
            )
        )

        self.rect = self.image.get_rect()

        self.rect.x = random.randrange(
            0,
            c.WIDTH - self.rect.width - 10,
            c.SIZE_OF_SBLOCK - 10
        )

        self.rect.y = random.randrange(
            0,
            c.HEIGHT - self.rect.height - 10,
            c.SIZE_OF_SBLOCK - 10
        )


class Enemy(pygame.sprite.Sprite):
    # squares to avoid
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(
            (
                c.SIZE_OF_SBLOCK,
                c.SIZE_OF_SBLOCK
            )
        )

        self.image.fill(c.RED)