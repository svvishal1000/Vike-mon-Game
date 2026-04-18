import pygame
import sys
import random
import os
import math
import cv2



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

def get_bounce_offset(speed=0.008, amount=16, phase=0):
    time = pygame.time.get_ticks()
    return int(math.sin(time * speed + phase) * amount)

# Screen settings
TILE_SIZE = 40
MAP_WIDTH = 20
MAP_HEIGHT = 15

WIDTH = TILE_SIZE * MAP_WIDTH
HEIGHT = TILE_SIZE * MAP_HEIGHT

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Vike'Mon")

game_surface = pygame.Surface((WIDTH, HEIGHT))

player_size = 30

def load_sprite(filename, width, height):
    """Load an image from the assets folder and scale it."""
    path = os.path.join("assets", filename)
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (width, height))
    return image

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
TEXT_COLOR = (0, 0, 0)
ENEMY_COLOR = (200, 50, 50)
BOX_COLOR = (220, 220, 220)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)

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



# -----------------------------
# Creature class
# -----------------------------
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

def get_tile_at_pixel(x, y):
    col = x // TILE_SIZE
    row = y // TILE_SIZE

    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        return game_map[row][col]

    return "#"

def can_move_to(x, y):
    corners = [
        (x, y),
        (x + player_size, y),
        (x, y + player_size),
        (x + player_size, y + player_size)
    ]

    for corner_x, corner_y in corners:
        tile = get_tile_at_pixel(corner_x, corner_y)
        if tile == "#":
            return False

    return True

def player_is_in_tall_grass():
    center_x = player_x + player_size // 2
    center_y = player_y + player_size // 2
    tile = get_tile_at_pixel(center_x, center_y)
    return tile == "G"

def draw_map():
    for row_index, row in enumerate(game_map):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            if tile == ".":
                game_surface.blit(ground_tile, (x, y))
            elif tile == "G":
                game_surface.blit(tall_grass_tile, (x, y))
            elif tile == "#":
                game_surface.blit(wall_tile, (x, y))

def draw_player():
    if player_direction == "down":
        sprite = player_down
    elif player_direction == "up":
        sprite = player_up
    elif player_direction == "left":
        sprite = player_left
    else:
        sprite = player_right

    offset = 0
    if is_moving:
        offset = -2 if (walk_timer // 8) % 2 == 0 else 0

    game_surface.blit(sprite, (player_x, player_y + offset))

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

def draw_flamethrower(start_x, start_y, end_x, end_y, progress):
    steps = 12

    for i in range(steps):
        t = i / steps

        if t > progress:
            break

        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)

        radius = max(4, 10 - i // 2)

        # Outer orange flame
        pygame.draw.circle(game_surface, (255, 140, 0), (x, y), radius)

        # Inner yellow flame
        pygame.draw.circle(game_surface, (255, 220, 80), (x, y), max(2, radius // 2))

def draw_thunderbolt(start_x, start_y, end_x, end_y):
    points = []
    segments = 6

    for i in range(segments + 1):
        t = i / segments
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)

        if 0 < i < segments:
            x += random.randint(-12, 12)
            y += random.randint(-12, 12)

        points.append((x, y))

    if len(points) >= 2:
        pygame.draw.lines(game_surface, (255, 255, 0), False, points, 4)
        pygame.draw.lines(game_surface, (255, 255, 200), False, points, 2)


def draw_battle_screen():
    game_surface.blit(battle_bg, (0, 0))

    enemy_bounce = get_bounce_offset(speed=0.008, amount=10, phase=0)
    player_bounce = get_bounce_offset(speed=0.008, amount=10, phase=3.14)

    enemy_shake_x = 0
    enemy_shake_y = 0
    player_shake_x = 0
    player_shake_y = 0

    enemy_attack_x = 0
    player_attack_x = 0

    if hit_timer > 0:
        shake_amount = 8 if hit_timer % 2 == 0 else -8

        if hit_target == "enemy":
            enemy_shake_x = shake_amount

        elif hit_target == "player":
            player_shake_x = shake_amount

    if attack_timer > 0:
        lunge_amount = 18

        if attack_attacker == "enemy":
            enemy_attack_x = -lunge_amount
        elif attack_attacker == "player":
            player_attack_x = lunge_amount        

    # Enemy creature
    enemy_x = 550 + enemy_shake_x + enemy_attack_x
    enemy_y = 210 + enemy_bounce + enemy_shake_y

    pygame.draw.ellipse(game_surface, (50, 50, 50), (enemy_x + 18, enemy_y + 72, 60, 20))
    game_surface.blit(enemy_creature.image, (enemy_x, enemy_y))

    draw_text(enemy_creature.name, 470, 80)
    draw_text(f"HP: {enemy_creature.hp}/{enemy_creature.max_hp}", 470, 110)
    draw_hp_bar(470, 140, enemy_creature.hp, enemy_creature.max_hp)

    # Player creature
    player_x_pos = 180 + player_shake_x + player_attack_x
    player_y_pos = 330 + player_bounce + player_shake_y

    pygame.draw.ellipse(game_surface, (50, 50, 50), (player_x_pos + 20, player_y_pos + 80, 80, 25))
    game_surface.blit(player_creature.image, (player_x_pos, player_y_pos))

    if move_effect == "flamethrower" and move_effect_timer > 0:
        progress = 1 - (move_effect_timer / 18)

        start_x = player_x_pos + 70
        start_y = player_y_pos + 35
        end_x = enemy_x + 30
        end_y = enemy_y + 35

        draw_flamethrower(start_x, start_y, end_x, end_y, progress)
    
    if move_effect == "thunderbolt" and move_effect_timer > 0:
        start_x = player_x_pos + 70
        start_y = player_y_pos + 35
        end_x = enemy_x + 30
        end_y = enemy_y + 35

        draw_thunderbolt(start_x, start_y, end_x, end_y)


    draw_text(player_creature.name, 70, 210)
    draw_text(f"HP: {player_creature.hp}/{player_creature.max_hp}", 70, 240)
    draw_hp_bar(70, 270, player_creature.hp, player_creature.max_hp)

    # Battle UI
    pygame.draw.rect(game_surface, BOX_COLOR, (40, 430, 720, 130))
    pygame.draw.rect(game_surface, BLACK, (40, 430, 720, 130), 2)

    draw_text(battle_message, 60, 455)
    draw_text("Press A = Attack    Press R = Run", 60, 500)

def enemy_turn():
    global battle_message, game_state, battle_result_timer
    global hit_target, hit_timer, attack_attacker, attack_timer

    damage = enemy_creature.attack_damage()
    player_creature.hp = max(0, player_creature.hp - damage)
    
    attack_attacker = "enemy"
    attack_timer = 10

    hit_target = "player"
    hit_timer = 12

    battle_message = f"{enemy_creature.name} attacks for {damage} damage!"

    if player_creature.is_fainted():
        battle_message = f"{player_creature.name} fainted! You lost!"
        game_state = "battle_end"
        battle_result_timer = 120

def play_intro_video():
    cap = cv2.VideoCapture("intro.mp4")

    if not cap.isOpened():
        print("Error: Could not open video")
        return

    # Get the video's real FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_delay = int(1000 / fps)

    # Play audio separately
    try:
        pygame.mixer.music.load("intro.mp3")
        pygame.mixer.music.play()
    except:
        print("Warning: Could not load intro.mp3")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        game_surface.blit(pygame_frame, (0, 0))

        # Scale to fullscreen while keeping aspect ratio
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

        # Skip intro
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    cap.release()
                    pygame.mixer.music.stop()
                    return
            elif event.type == pygame.QUIT:
                cap.release()
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

        # This is what slows playback to the correct speed
        pygame.time.wait(frame_delay)

    cap.release()
    pygame.mixer.music.stop()
    

def play_title_menu():
    cap = cv2.VideoCapture("title_menu.mp4")

    if not cap.isOpened():
        print("Error: Could not open title_menu.mp4")
        return "new_game"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_delay = int(1000 / fps)

    try:
        pygame.mixer.music.load("title_menu.mp3")
        pygame.mixer.music.play(-1)  # loop music
    except:
        print("Warning: Could not load title_menu.mp3")

    options = ["New Game", "Continue", "Exit"]
    selected_option = 0

    while True:
        ret, frame = cap.read()

        # loop video if it ends
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        game_surface.blit(pygame_frame, (0, 0))

        # dark overlay so text is readable
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        game_surface.blit(overlay, (0, 0))

        # title
        # Floating effect
        logo_y = 80 + int(math.sin(pygame.time.get_ticks() * 0.002) * 5)

        # Scale pulse
        scale = 1 + (math.sin(pygame.time.get_ticks() * 0.003) * 0.02)

        scaled_logo = pygame.transform.scale(
            title_logo,
            (int(420 * scale), int(140 * scale))
        )

        scaled_x = 80  # left aligned

        # Draw logo only (no glow)
        game_surface.blit(scaled_logo, (scaled_x, logo_y))

        # Sparkle
        if int(pygame.time.get_ticks() * 0.01) % 40 == 0:
            sparkle_x = scaled_x + scaled_logo.get_width() - 30
            sparkle_y = logo_y + 18

            pygame.draw.circle(game_surface, (255, 255, 255), (sparkle_x, sparkle_y), 3)
            pygame.draw.circle(game_surface, (255, 255, 180), (sparkle_x, sparkle_y), 6, 1)

        # menu options
        menu_x = 520
        start_y = 260
        line_spacing = 60

        for i, option in enumerate(options):
            y = start_y + i * line_spacing

            if i == selected_option:
                # 🔥 brightness pulse (color oscillation)
                pulse = int(55 * (math.sin(pygame.time.get_ticks() * 0.005) + 1))
                color = (255, 255, 200 + pulse // 2)

                # 🔥 slight scale effect
                scale = 1 + (math.sin(pygame.time.get_ticks() * 0.005) * 0.05)

                option_surface = font.render(option, True, color)
                scaled_option = pygame.transform.scale(
                    option_surface,
                    (
                        int(option_surface.get_width() * scale),
                        int(option_surface.get_height() * scale)
                    )
                )

                # adjust position so it doesn’t shift when scaling
                draw_x = menu_x
                draw_y = y - (scaled_option.get_height() - option_surface.get_height()) // 2

                # arrow
                arrow = font.render("@", True, HIGHLIGHT_COLOR)
                game_surface.blit(arrow, (menu_x - 40, y))

                game_surface.blit(scaled_option, (draw_x, draw_y))

            else:
                color = (200, 200, 200)  # dim inactive options
                option_text = font.render(option, True, color)
                game_surface.blit(option_text, (menu_x, y))

        # hint text
        hint_text = font.render("Use UP/DOWN and ENTER", True, WHITE)
        game_surface.blit(hint_text, (470, 500))
        

        # scale to fullscreen
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    if menu_move_sound:
                        menu_move_sound.play()

                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    if menu_move_sound:
                        menu_move_sound.play()

                elif event.key == pygame.K_RETURN:
                    if menu_select_sound:
                        menu_select_sound.play()

                    pygame.time.delay(150)  # lets sound play before switching

                    cap.release()
                    pygame.mixer.music.stop()

                    if selected_option == 0:
                        return "new_game"
                    elif selected_option == 1:
                        return "continue"
                    else:
                        pygame.quit()
                        sys.exit()

                elif event.key == pygame.K_ESCAPE:
                    cap.release()
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()

        pygame.time.wait(frame_delay)


play_intro_video()
menu_choice = play_title_menu()

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
                        enemy_turn()

                elif event.key == pygame.K_r:
                    if random.randint(1, 100) <= 75:
                        battle_message = "You ran away safely!"
                        game_state = "battle_end"
                        battle_result_timer = 60
                    else:
                        battle_message = "Could not escape!"
                        enemy_turn()

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

        if can_move_to(new_x, player_y):
            if new_x != player_x:
                moved = True
            player_x = new_x

        if can_move_to(player_x, new_y):
            if new_y != player_y:
                moved = True
            player_y = new_y

        if is_moving:
            walk_timer += 1
        else:
            walk_timer = 0

        if moved and player_is_in_tall_grass():
            if random.randint(1, 100) <= 2:
                start_battle()

        draw_map()
        draw_player()

    elif game_state == "battle":
        draw_battle_screen()

    elif game_state == "battle_end":
        draw_battle_screen()
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