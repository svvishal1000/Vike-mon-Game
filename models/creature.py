import random
from utils.helpers import load_sprite


class Creature:
    def __init__(self, name, max_hp, attack_min, attack_max, image_file):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack_min = attack_min
        self.attack_max = attack_max
        self.image_file = image_file

        # 🔥 enable sprite loading again
        self.image = load_sprite(image_file, 90, 90)

        # keep color as fallback (optional)
        self.color = (200, 50, 50)

    def attack_damage(self):
        return random.randint(self.attack_min, self.attack_max)

    def heal_full(self):
        self.hp = self.max_hp

    def is_fainted(self):
        return self.hp <= 0