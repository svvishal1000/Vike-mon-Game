import random
from utils.helpers import load_sprite

class Creature:
    def __init__(self, name, creature_type, max_hp, attack_min, attack_max, image_file, moves):
        self.name = name
        self.creature_type = creature_type
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack_min = attack_min
        self.attack_max = attack_max
        self.image_file = image_file
        self.image = load_sprite(image_file, 90, 90)
        self.color = (200, 50, 50)
        self.moves = moves

    def attack_damage(self, move_power=0):
        return random.randint(self.attack_min, self.attack_max) + move_power

    def heal_full(self):
        self.hp = self.max_hp

    def is_fainted(self):
        return self.hp <= 0