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

# Load images
title_logo = load_sprite("title_logo.png", 500, 200)

battle_bg = pygame.image.load("assets/battle_bg.png").convert()
battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))

# ⭐ ADD THIS RIGHT BELOW
starter_bg = pygame.image.load("assets/starter_bg.png").convert()


# Tile and sprite images
ground_tile = load_sprite("ground.png", TILE_SIZE, TILE_SIZE)
tall_grass_tile = load_sprite("tall_grass.png", TILE_SIZE, TILE_SIZE)
wall_tile = load_sprite("wall.png", TILE_SIZE, TILE_SIZE)
battle_bg = load_sprite("battle_bg.png", WIDTH, HEIGHT)

# player_sprite = load_sprite("player.png", player_size, player_size)


clock = pygame.time.Clock()
font_small = pygame.font.Font("assets/fonts/Orbitron.ttf", 20)
font_large = pygame.font.Font("assets/fonts/Orbitron.ttf", 40)
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
    selected_font = font_large if use_big_font else font_small
    text_surface = selected_font.render(text, True, color)
    game_surface.blit(text_surface, (x, y))

def draw_hp_bar(x, y, current_hp, max_hp, width=200, height=20):
    # Background (light gray)
    pygame.draw.rect(game_surface, (230, 235, 240), (x, y, width, height), border_radius=8)

    # Border
    pygame.draw.rect(game_surface, (40, 40, 50), (x, y, width, height), 2, border_radius=8)

    # HP ratio
    hp_ratio = max(0, current_hp / max_hp)

    # 🎨 Color logic
    if hp_ratio > 0.7:
        hp_color = (80, 220, 120)     # Green
    elif hp_ratio > 0.3:
        hp_color = (255, 190, 60)    # Yellow
    else:
        hp_color = (220, 70, 70)     # Red
        # optional glow
        if pygame.time.get_ticks() // 200 % 2 == 0:
            hp_color = (255, 90, 90)

    # Inner bar width
    inner_width = int((width - 4) * hp_ratio)

    # Draw HP bar
    if inner_width > 0:
        pygame.draw.rect(
            game_surface,
            hp_color,
            (x + 2, y + 2, inner_width, height - 4),
            border_radius=6
        )


def draw_type_badge(surface, text, center_x, y):
    type_name = text.lower()

    badge_colors = {
        "fire": (255, 140, 0),       # orange
        "water": (70, 130, 255),     # blue
        "grass": (60, 170, 80),      # green
        "electric": (240, 200, 0),   # yellow
        "normal": (150, 150, 150),   # gray
    }

    bg_color = badge_colors.get(type_name, badge_colors["normal"])

    badge_font = pygame.font.Font("assets/fonts/Orbitron.ttf", 16)
    text_surface = badge_font.render(text.upper(), True, (255, 255, 255))
    text_rect = text_surface.get_rect()

    padding_x = 14
    padding_y = 6

    badge_width = text_rect.width + padding_x * 2
    badge_height = text_rect.height + padding_y * 2

    badge_rect = pygame.Rect(0, 0, badge_width, badge_height)
    badge_rect.centerx = center_x
    badge_rect.y = y

    # solid background
    pygame.draw.rect(surface, bg_color, badge_rect, border_radius=12)

    # subtle border (slightly darker)
    darker = tuple(max(0, c - 40) for c in bg_color)
    pygame.draw.rect(surface, darker, badge_rect, 2, border_radius=12)

    # text
    text_rect.center = badge_rect.center
    surface.blit(text_surface, text_rect)


def draw_starter_screen():
    # background
    game_surface.blit(starter_bg, (0, 0))

    # dark overlay so cards/text stand out
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    game_surface.blit(overlay, (0, 0))

    # colors
    CARD_BG = (245, 248, 252)
    CARD_SHADOW = (20, 20, 30, 80)
    CARD_BORDER = (120, 135, 155)
    SELECTED_BORDER = (135, 206, 235)
    SELECTED_GLOW = (180, 225, 245, 90)
    TITLE_COLOR = (235, 245, 255)
    TEXT_COLOR_SOFT = (35, 45, 60)
    SUBTEXT_COLOR = (210, 225, 240)

    # title
    title = font_large.render("Choose Your Starter", True, TITLE_COLOR)
    title_rect = title.get_rect(center=(WIDTH // 2, 75))
    game_surface.blit(title, title_rect)

    subtitle = font_small.render(
        "Use LEFT / RIGHT to choose, ENTER to confirm",
        True,
        SUBTEXT_COLOR
    )
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 115))
    game_surface.blit(subtitle, subtitle_rect)

    # layout
    card_width = 180
    card_height = 255
    gap = 35
    total_width = len(starter_choices) * card_width + (len(starter_choices) - 1) * gap
    start_x = (WIDTH - total_width) // 2
    card_y = 180

    for i, creature in enumerate(starter_choices):
        x = start_x + i * (card_width + gap)
        y = card_y

        selected = (i == selected_starter_index)
        border_color = SELECTED_BORDER if selected else CARD_BORDER

        # glow behind selected card
        if selected:
            glow = pygame.Surface((card_width + 18, card_height + 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, SELECTED_GLOW, glow.get_rect(), border_radius=24)
            game_surface.blit(glow, (x - 9, y - 9))

        # shadow
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, CARD_SHADOW, shadow.get_rect(), border_radius=18)
        game_surface.blit(shadow, (x + 6, y + 8))

        # card
        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(game_surface, CARD_BG, card_rect, border_radius=18)
        pygame.draw.rect(game_surface, border_color, card_rect, width=4, border_radius=18)

        # creature image with tiny bounce for selected one
        preview_size = 92 if selected else 82
        bounce = -4 if selected and (pygame.time.get_ticks() // 180) % 2 == 0 else 0
        preview_image = pygame.transform.smoothscale(creature.image, (preview_size, preview_size))
        img_rect = preview_image.get_rect(center=(x + card_width // 2, y + 76 + bounce))
        game_surface.blit(preview_image, img_rect)

        # text
        name_surface = font_small.render(creature.name, True, TEXT_COLOR_SOFT)
        name_rect = name_surface.get_rect(center=(x + card_width // 2, y + 142))
        game_surface.blit(name_surface, name_rect)

        badge_y = y + 156

        if selected:
            badge_y -= 2  # slight lift for selected

        draw_type_badge(
            game_surface,
            creature.creature_type,
            x + card_width // 2,
            badge_y
        )

        hp_surface = font_small.render(f"HP: {creature.max_hp}", True, TEXT_COLOR_SOFT)
        hp_rect = hp_surface.get_rect(center=(x + card_width // 2, y + 210))
        game_surface.blit(hp_surface, hp_rect)

        atk_surface = font_small.render(
            f"ATK: {creature.attack_min}-{creature.attack_max}",
            True,
            TEXT_COLOR_SOFT
        )
        atk_rect = atk_surface.get_rect(center=(x + card_width // 2, y + 238))
        game_surface.blit(atk_surface, atk_rect)

    # bottom help box
    help_rect = pygame.Rect(WIDTH // 2 - 215, HEIGHT - 76, 430, 48)
    pygame.draw.rect(game_surface, (225, 240, 248), help_rect, border_radius=14)
    pygame.draw.rect(game_surface, (135, 206, 235), help_rect, width=3, border_radius=14)

    help_text = font_small.render("Press ENTER to begin your adventure", True, (35, 45, 60))
    help_text_rect = help_text.get_rect(center=help_rect.center)
    game_surface.blit(help_text, help_text_rect)


# Play intro video once at startup
play_intro_video(screen, game_surface, pygame.mixer, clock)

menu_choice = play_title_menu(
    screen,
    game_surface,
    pygame.mixer,
    clock,
    title_logo,
    font_small,
    ["New Game", "Continue", "Exit"],
    menu_move_sound,
    menu_select_sound,
)

if menu_choice == "new_game":
    play_welcome_video(screen, game_surface, font_large)
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
            draw_type_badge,
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
            draw_type_badge,
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