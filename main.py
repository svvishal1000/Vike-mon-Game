import sys
import pygame
import random

from settings import *
from utils.helpers import load_sprite, get_bounce_offset
from models.creature import Creature
from systems.battle import draw_battle_screen, enemy_turn
from video_menu import play_intro_video, play_title_menu
from systems.overworld import (
    can_move_to,
    player_is_in_tall_grass,
    draw_map,
    draw_player,
)


# Start pygame
pygame.init()

pygame.mixer.init()

try:
    menu_move_sound = pygame.mixer.Sound("menu_move.mp3")
    menu_select_sound = pygame.mixer.Sound("menu_select.mp3")

    menu_move_sound.set_volume(0.4)
    menu_select_sound.set_volume(0.5)
except:
    menu_move_sound = None
    menu_select_sound = None


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Vike'Mon")

game_surface = pygame.Surface((WIDTH, HEIGHT))

player_size = 30



# Tile and sprite images
ground_tile = load_sprite("ground.png", TILE_SIZE, TILE_SIZE)
tall_grass_tile = load_sprite("tall_grass.png", TILE_SIZE, TILE_SIZE)
wall_tile = load_sprite("wall.png", TILE_SIZE, TILE_SIZE)
battle_bg = load_sprite("battle_bg.png", WIDTH, HEIGHT)

# player_sprite = load_sprite("player.png", player_size, player_size)


clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 40)

# Colors
GROUND_COLOR = (34, 177, 76)
TALL_GRASS_COLOR = (0, 120, 0)
WALL_COLOR = (100, 70, 30)
GRID_COLOR = (20, 140, 50)
PLAYER_COLOR = (0, 0, 255)
BATTLE_BG_COLOR = (240, 240, 240)

ENEMY_COLOR = (200, 50, 50)



# Map data
game_map = [
    "####################",
    "#.............GG...#",
    "#.............GG...#",
    "#..GGGG............#",
    "#..GGGG............#",
    "#..........#####...#",
    "#..................#",
    "#......GGGG........#",
    "#......GGGG........#",
    "#..................#",
    "#...#####..........#",
    "#..................#",
    "#..............GG..#",
    "#..............GG..#",
    "####################"
]

# Player settings
player_x = 2 * TILE_SIZE
player_y = 2 * TILE_SIZE
player_size = 40
player_down = load_sprite("player_down.png", player_size, player_size)
player_up = load_sprite("player_up.png", player_size, player_size)
player_left = load_sprite("player_left.png", player_size, player_size)
player_right = load_sprite("player_right.png", player_size, player_size)
title_logo = load_sprite("title_logo.png", 500, 200)

player_direction = "down"
player_speed = 5

walk_timer = 0
is_moving = False



# Starter choices
starter_choices = [
    Creature("Pyroo", 30, 4, 8, "pyroo.png"),
    Creature("Aquaff", 32, 3, 7, "aquaff.png"),
    Creature("Spriglet", 28, 5, 9, "spriglet.png")
]

selected_starter_index = 0
player_creature = None

# Wild creature choices
wild_creature_templates = [
    Creature("Leafling", 20, 3, 6, "leafling.png"),
    Creature("Aquaff", 22, 2, 5, "aquaff.png"),
    Creature("Sparkit", 18, 4, 7, "sparkit.png"),
    Creature("Flamix", 26, 5, 9, "flamix.png")
]

enemy_creature = None

# Game state
game_state = "title_screen"

battle_message = "A wild creature appeared!"
battle_result_timer = 0

hit_target = None
hit_timer = 0

attack_attacker = None
attack_timer = 0

move_effect = None
move_effect_timer = 0

def clone_creature(creature):
    return Creature(
        creature.name,
        creature.max_hp,
        creature.attack_min,
        creature.attack_max,
        creature.image_file
    )

def create_wild_creature():
    """Return a fresh copy of a random wild creature."""
    template = random.choice(wild_creature_templates)
    return clone_creature(template)

def start_battle():
    """Start a new battle with a random wild creature."""
    global game_state, enemy_creature, battle_message, battle_result_timer

    enemy_creature = create_wild_creature()
    game_state = "battle"
    battle_message = f"A wild {enemy_creature.name} appeared!"
    battle_result_timer = 0


def draw_text(text, x, y, use_big_font=False, color=TEXT_COLOR):
    selected_font = big_font if use_big_font else font
    text_surface = selected_font.render(text, True, color)
    game_surface.blit(text_surface, (x, y))

def draw_hp_bar(x, y, current_hp, max_hp, width=200, height=20):
    pygame.draw.rect(game_surface, BLACK, (x, y, width, height), 2)

    hp_ratio = current_hp / max_hp
    inner_width = int((width - 4) * hp_ratio)

    pygame.draw.rect(game_surface, (0, 200, 0), (x + 2, y + 2, inner_width, height - 4))

def draw_starter_screen():
    game_surface.fill((230, 230, 255))

    draw_text("Choose Your Starter", 260, 60, use_big_font=True)
    draw_text("Use LEFT / RIGHT to choose, ENTER to confirm", 170, 110)

    start_x = 140
    gap = 220

    for i, creature in enumerate(starter_choices):
        x = start_x + i * gap
        y = 250

        border_color = HIGHLIGHT_COLOR if i == selected_starter_index else BLACK

        pygame.draw.rect(game_surface, WHITE, (x - 40, y - 90, 140, 200))
        pygame.draw.rect(game_surface, border_color, (x - 40, y - 90, 140, 200), 4)

        preview_image = pygame.transform.scale(creature.image, (70, 70))
        game_surface.blit(preview_image, (x - 5, y - 35))

        draw_text(creature.name, x - 10, y + 60)
        draw_text(f"HP: {creature.max_hp}", x - 10, y + 95)
        draw_text(f"ATK: {creature.attack_min}-{creature.attack_max}", x - 10, y + 130)


play_intro_video(screen, game_surface, pygame.mixer, clock)

menu_choice = play_title_menu(
    screen,
    game_surface,
    pygame.mixer,
    clock,
    title_logo,
    font,
    ["New Game", "Continue", "Exit"],
    menu_move_sound,
    menu_select_sound,
)

if menu_choice == "new_game":
    game_state = "starter_select"
elif menu_choice == "continue":
    game_state = "starter_select"



# Main game loop
running = True

while running:
    moved = False
    game_surface.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if game_state == "starter_select":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_starter_index = max(0, selected_starter_index - 1)

                elif event.key == pygame.K_RIGHT:
                    selected_starter_index = min(len(starter_choices) - 1, selected_starter_index + 1)

                elif event.key == pygame.K_RETURN:
                    player_creature = clone_creature(starter_choices[selected_starter_index])
                    game_state = "overworld"

        elif game_state == "battle":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    damage = player_creature.attack_damage()
                    enemy_creature.hp = max(0, enemy_creature.hp - damage)
                    
                    attack_attacker = "player"
                    attack_timer = 10

                    move_effect = "flamethrower"
                    move_effect_timer = 18

                    #move_effect = "thunderbolt"
                    #move_effect_timer = 8

                    hit_target = "enemy"
                    hit_timer = 12

                    if enemy_creature.is_fainted():
                        battle_message = f"You defeated {enemy_creature.name}!"
                        game_state = "battle_end"
                        battle_result_timer = 120
                    else:
                        battle_message = f"{player_creature.name} attacks for {damage} damage!"
                        result = enemy_turn(
                            enemy_creature,
                            player_creature,
                            battle_result_timer,
                        )

                        battle_message = result["battle_message"]
                        hit_target = result["hit_target"]
                        hit_timer = result["hit_timer"]
                        attack_attacker = result["attack_attacker"]
                        attack_timer = result["attack_timer"]

                        if result["game_state"] is not None:
                            game_state = result["game_state"]
                            battle_result_timer = result["battle_result_timer"]

                elif event.key == pygame.K_r:
                    if random.randint(1, 100) <= 75:
                        battle_message = "You ran away safely!"
                        game_state = "battle_end"
                        battle_result_timer = 60
                    else:
                        battle_message = "Could not escape!"
                        result = enemy_turn(
                            enemy_creature,
                            player_creature,
                            battle_result_timer,
                        )

                        battle_message = result["battle_message"]
                        hit_target = result["hit_target"]
                        hit_timer = result["hit_timer"]
                        attack_attacker = result["attack_attacker"]
                        attack_timer = result["attack_timer"]

                        if result["game_state"] is not None:
                            game_state = result["game_state"]
                            battle_result_timer = result["battle_result_timer"]

    if game_state == "starter_select":
        draw_starter_screen()

    elif game_state == "overworld":
        keys = pygame.key.get_pressed()

        new_x = player_x
        new_y = player_y

        is_moving = False

        if keys[pygame.K_LEFT]:
            new_x -= player_speed
            player_direction = "left"
            is_moving = True

        if keys[pygame.K_RIGHT]:
            new_x += player_speed
            player_direction = "right"
            is_moving = True

        if keys[pygame.K_UP]:
            new_y -= player_speed
            player_direction = "up"
            is_moving = True

        if keys[pygame.K_DOWN]:
            new_y += player_speed
            player_direction = "down"
            is_moving = True

        if can_move_to(new_x, player_y, player_size, game_map):
            if new_x != player_x:
                moved = True
            player_x = new_x

        if can_move_to(player_x, new_y, player_size, game_map):
            if new_y != player_y:
                moved = True
            player_y = new_y

        if is_moving:
            walk_timer += 1
        else:
            walk_timer = 0

        if moved and player_is_in_tall_grass(player_x, player_y, player_size, game_map):
            if random.randint(1, 100) <= 2:
                start_battle()

        draw_map(game_surface, game_map, ground_tile, tall_grass_tile, wall_tile)
        draw_player(
            game_surface,
            player_x,
            player_y,
            player_direction,
            is_moving,
            walk_timer,
            player_down,
            player_up,
            player_left,
            player_right,
        )

    elif game_state == "battle":
        draw_battle_screen(
            game_surface,
            battle_bg,
            enemy_creature,
            player_creature,
            battle_message,
            hit_timer,
            hit_target,
            attack_timer,
            attack_attacker,
            move_effect,
            move_effect_timer,
            get_bounce_offset,
            draw_text,
            draw_hp_bar,
        )

    elif game_state == "battle_end":
        draw_battle_screen(
            game_surface,
            battle_bg,
            enemy_creature,
            player_creature,
            battle_message,
            hit_timer,
            hit_target,
            attack_timer,
            attack_attacker,
            move_effect,
            move_effect_timer,
            get_bounce_offset,
            draw_text,
            draw_hp_bar,
        )

        battle_result_timer -= 1

        if battle_result_timer <= 0:
            if player_creature.is_fainted():
                player_creature.heal_full()
                player_x = 2 * TILE_SIZE
                player_y = 2 * TILE_SIZE

            game_state = "overworld"
    if hit_timer > 0:
        hit_timer -= 1
    if attack_timer > 0:
        attack_timer -= 1
    if move_effect_timer > 0:
        move_effect_timer -= 1
    else:
        move_effect = None        

    screen_width, screen_height = screen.get_size()

    scale_x = screen_width / WIDTH
    scale_y = screen_height / HEIGHT
    scale_factor = min(scale_x, scale_y)

    scaled_width = int(WIDTH * scale_factor)
    scaled_height = int(HEIGHT * scale_factor)

    scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))

    x_offset = (screen_width - scaled_width) // 2
    y_offset = (screen_height - scaled_height) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()