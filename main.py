import sys
import pygame
import random

from settings import *
from utils.helpers import load_sprite, get_bounce_offset
from models.creature import Creature
from models.move import Move
from systems.battle import draw_battle_screen, enemy_turn, calculate_move_damage
from video_menu import play_intro_video, play_title_menu, play_welcome_video
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

pyroo_moves = [
    Move("Scratch", 2, "normal", "none"),
    Move("Ember", 4, "fire", "flamethrower"),
    Move("Fire Fang", 5, "fire", "flamethrower"),
    Move("Flame Burst", 6, "fire", "flamethrower"),
]

flamix_moves = [
    Move("Tackle", 2, "normal", "none"),
    Move("Spark Ember", 4, "fire", "flamethrower"),
    Move("Flare Kick", 5, "fire", "flamethrower"),
    Move("Inferno", 7, "fire", "flamethrower"),
]

aquaff_moves = [
    Move("Splash Hit", 2, "water", "none"),
    Move("Bubble Shot", 4, "water", "none"),
    Move("Water Pulse", 5, "water", "none"),
    Move("Aqua Crash", 6, "water", "none"),
]

leafling_moves = [
    Move("Leaf Tap", 2, "grass", "none"),
    Move("Vine Whip", 4, "grass", "none"),
    Move("Razor Leaf", 5, "grass", "none"),
    Move("Nature Burst", 6, "grass", "none"),
]

spriglet_moves = [
    Move("Seed Hit", 2, "grass", "none"),
    Move("Leaf Blade", 4, "grass", "none"),
    Move("Vine Lash", 5, "grass", "none"),
    Move("Bloom Strike", 6, "grass", "none"),
]

sparkit_moves = [
    Move("Quick Jab", 2, "normal", "none"),
    Move("Spark", 4, "electric", "thunderbolt"),
    Move("Thunder Jolt", 5, "electric", "thunderbolt"),
    Move("Thunderbolt", 7, "electric", "thunderbolt"),
]

# Starter choices
starter_choices = [
    Creature("Pyroo", "fire", 30, 4, 8, "pyroo.png", pyroo_moves),
    Creature("Aquaff", "water", 32, 3, 7, "aquaff.png", aquaff_moves),
    Creature("Spriglet", "grass", 28, 5, 9, "spriglet.png", spriglet_moves),
]

selected_starter_index = 0
player_creature = None

# Wild creature choices
wild_creature_templates = [
    Creature("Leafling", "grass", 20, 3, 6, "leafling.png", leafling_moves),
    Creature("Aquaff", "water", 22, 2, 5, "aquaff.png", aquaff_moves),
    Creature("Sparkit", "electric", 18, 4, 7, "sparkit.png", sparkit_moves),
    Creature("Flamix", "fire", 26, 5, 9, "flamix.png", flamix_moves),
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

# Battle UI state
battle_phase = "message"
battle_messages = []
battle_after_messages = "action_menu"

battle_menu_options = ["Attack", "Open Bag", "Throw a Rock", "Run"]
battle_menu_index = 0
move_menu_index = 0

def clone_creature(creature):
    return Creature(
        creature.name,
        creature.creature_type,
        creature.max_hp,
        creature.attack_min,
        creature.attack_max,
        creature.image_file,
        creature.moves
    )

def create_wild_creature():
    """Return a fresh copy of a random wild creature."""
    template = random.choice(wild_creature_templates)
    return clone_creature(template)

def start_battle():
    """Start a new battle with a random wild creature."""
    global game_state, enemy_creature, battle_message, battle_result_timer
    global battle_menu_index, move_menu_index

    enemy_creature = create_wild_creature()
    game_state = "battle"
    battle_result_timer = 0

    battle_menu_index = 0
    move_menu_index = 0

    set_battle_messages(
        [
            f"A wild {enemy_creature.name} appeared!",
            f"Go {player_creature.name}!",
        ],
        "action_menu"
    )

def set_battle_messages(messages, after_phase="action_menu"):
    global battle_phase, battle_messages, battle_after_messages
    battle_phase = "message"
    battle_messages = list(messages)
    battle_after_messages = after_phase


def run_enemy_turn_sequence():
    global battle_message, game_state, battle_result_timer
    global hit_target, hit_timer, attack_attacker, attack_timer
    global move_effect, move_effect_timer

    result = enemy_turn(
        enemy_creature,
        player_creature,
        battle_result_timer,
    )

    hit_target = result["hit_target"]
    hit_timer = result["hit_timer"]
    attack_attacker = result["attack_attacker"]
    attack_timer = result["attack_timer"]
    move_effect = result["move_effect"]
    move_effect_timer = result["move_effect_timer"]

    enemy_messages = [result["battle_message"]]

    if result["game_state"] == "battle_end":
        game_state = "battle_end"
        battle_result_timer = result["battle_result_timer"]
        battle_message = result["battle_message"]
    else:
        set_battle_messages(enemy_messages, "action_menu")


def advance_battle_messages():
    global battle_phase, battle_messages, battle_after_messages
    global game_state, battle_result_timer, battle_message

    if battle_messages:
        battle_messages.pop(0)

    if battle_messages:
        return

    if battle_after_messages == "enemy_turn":
        run_enemy_turn_sequence()
    elif battle_after_messages == "end_win":
        battle_message = "You won the battle!"
        game_state = "battle_end"
        battle_result_timer = 120
    elif battle_after_messages == "end_loss":
        game_state = "battle_end"
        battle_result_timer = 120
    else:
        battle_phase = battle_after_messages


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
    play_welcome_video(screen, game_surface, font)
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

                if battle_phase == "message":
                    if event.key == pygame.K_RETURN:
                        advance_battle_messages()

                elif battle_phase == "action_menu":
                    if event.key == pygame.K_LEFT and battle_menu_index in [1, 3]:
                        battle_menu_index -= 1
                    elif event.key == pygame.K_RIGHT and battle_menu_index in [0, 2]:
                        battle_menu_index += 1
                    elif event.key == pygame.K_UP and battle_menu_index in [2, 3]:
                        battle_menu_index -= 2
                    elif event.key == pygame.K_DOWN and battle_menu_index in [0, 1]:
                        battle_menu_index += 2

                    elif event.key == pygame.K_RETURN:
                        selected_action = battle_menu_options[battle_menu_index]

                        if selected_action == "Attack":
                            battle_phase = "move_menu"

                        elif selected_action == "Open Bag":
                            set_battle_messages(["Your bag is empty right now."], "action_menu")

                        elif selected_action == "Throw a Rock":
                            enemy_creature.hp = max(0, enemy_creature.hp - 1)
                            set_battle_messages(["You threw a rock! It did 1 damage."], "enemy_turn")

                        elif selected_action == "Run":
                            if random.randint(1, 100) <= 75:
                                battle_message = "You ran away safely!"
                                game_state = "battle_end"
                                battle_result_timer = 60
                            else:
                                set_battle_messages(["Could not escape!"], "enemy_turn")

                elif battle_phase == "move_menu":
                    if event.key == pygame.K_LEFT and move_menu_index in [1, 3]:
                        move_menu_index -= 1
                    elif event.key == pygame.K_RIGHT and move_menu_index in [0, 2]:
                        move_menu_index += 1
                    elif event.key == pygame.K_UP and move_menu_index in [2, 3]:
                        move_menu_index -= 2
                    elif event.key == pygame.K_DOWN and move_menu_index in [0, 1]:
                        move_menu_index += 2
                    elif event.key == pygame.K_ESCAPE:
                        battle_phase = "action_menu"

                    elif event.key == pygame.K_RETURN:
                        move = player_creature.moves[move_menu_index]
                        damage, multiplier = calculate_move_damage(player_creature, enemy_creature, move)
                        enemy_creature.hp = max(0, enemy_creature.hp - damage)

                        attack_attacker = "player"
                        attack_timer = 10

                        move_effect = move.animation
                        if move.animation == "flamethrower":
                            move_effect_timer = 18
                        elif move.animation == "thunderbolt":
                            move_effect_timer = 8
                        else:
                            move_effect_timer = 0

                        hit_target = "enemy"
                        hit_timer = 12

                        messages = [f"{player_creature.name} used {move.name}!"]

                        if multiplier > 1.0:
                            messages.append("It's super effective!")
                        elif multiplier < 1.0:
                            messages.append("It's not very effective...")

                        if enemy_creature.is_fainted():
                            messages.append(f"You defeated {enemy_creature.name}!")
                            set_battle_messages(messages, "end_win")
                        else:
                            set_battle_messages(messages, "enemy_turn")

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
        current_battle_message = battle_messages[0] if battle_messages else battle_message
        
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
            battle_phase,
            current_battle_message,
            battle_menu_options,
            battle_menu_index,
            move_menu_index,
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
            battle_phase,
            current_battle_message,
            battle_menu_options,
            battle_menu_index,
            move_menu_index,
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