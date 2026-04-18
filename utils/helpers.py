import os
import pygame
import math

def load_sprite(filename, width, height):
    """Load an image from the assets folder and scale it."""
    path = os.path.join("assets", filename)
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (width, height))
    return image

def get_bounce_offset(speed=0.008, amount=16, phase=0):
    time = pygame.time.get_ticks()
    return int(math.sin(time * speed + phase) * amount)
