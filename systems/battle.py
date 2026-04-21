import random
import pygame

from settings import BLACK, BOX_COLOR, WHITE

TYPE_EFFECTIVENESS = {
    # Super effective
    ("fire", "grass"): 2.0,
    ("water", "fire"): 2.0,
    ("grass", "water"): 2.0,
    ("electric", "water"): 2.0,

    # Not very effective
    ("water", "grass"): 0.5,
    ("fire", "water"): 0.5,
    ("grass", "fire"): 0.5,
}

def get_type_multiplier(move_type, defender_type):
    return TYPE_EFFECTIVENESS.get((move_type, defender_type), 1.0)


def calculate_move_damage(attacker, defender, move):
    base_damage = attacker.attack_damage(move.power)
    multiplier = get_type_multiplier(move.move_type, defender.creature_type)
    final_damage = int(base_damage * multiplier)
    return max(1, final_damage), multiplier


def draw_flamethrower(game_surface, start_x, start_y, end_x, end_y, progress):
    steps = 12

    for i in range(steps):
        t = i / steps

        if t > progress:
            break

        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)

        radius = max(4, 10 - i // 2)

        pygame.draw.circle(game_surface, (255, 140, 0), (x, y), radius)
        pygame.draw.circle(game_surface, (255, 220, 80), (x, y), max(2, radius // 2))


def draw_thunderbolt(game_surface, start_x, start_y, end_x, end_y):
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


def draw_info_panel(surface, x, y, w, h, border_color):
    panel_rect = pygame.Rect(x, y, w, h)

    # Create gradient surface
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)

    top_color = (255, 255, 255, 160)   # lighter
    bottom_color = (240, 245, 250, 140)  # slightly darker

    # Dark-Mode
    # top_color = (60, 70, 85, 200)
    # bottom_color = (30, 35, 45, 200)

    for i in range(h):
        ratio = i / h

        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        a = int(top_color[3] * (1 - ratio) + bottom_color[3] * ratio)

        pygame.draw.line(gradient, (r, g, b, a), (0, i), (w, i))

    # Rounded mask effect
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=14)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    surface.blit(gradient, (x, y))

    # subtle border
    pygame.draw.rect(surface, border_color, panel_rect, 2, border_radius=14)

    return panel_rect


def draw_stat_text(surface, font_obj, text, x, y, color=(35, 45, 60)):
    text_surface = font_obj.render(text, True, color)
    surface.blit(text_surface, (x, y))


def draw_battle_screen(
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
    draw_type_badge,   # 👈 ADD THIS
    battle_phase,
    current_battle_message,
    battle_menu_options,
    battle_menu_index,
    move_menu_index,
):


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

    enemy_x = 550 + enemy_shake_x + enemy_attack_x
    enemy_y = 210 + enemy_bounce + enemy_shake_y

    pygame.draw.ellipse(game_surface, (50, 50, 50), (enemy_x + 18, enemy_y + 72, 60, 20))
    game_surface.blit(enemy_creature.image, (enemy_x, enemy_y))

    name_font = pygame.font.Font("assets/fonts/Orbitron.ttf", 20)
    stat_font = pygame.font.Font("assets/fonts/Orbitron.ttf", 16)

    enemy_panel = draw_info_panel(game_surface, 440, 58, 235, 100, (135, 206, 235))

    # Name (left)
    draw_stat_text(
        game_surface,
        name_font,
        enemy_creature.name,
        enemy_panel.x + 12,
        enemy_panel.y + 10
    )

    # Type badge (right side of name)
    draw_type_badge(
        game_surface,
        enemy_creature.creature_type,
        enemy_panel.x + 170,
        enemy_panel.y + 10
    )

    # HP bar (left bottom)
    draw_hp_bar(
        enemy_panel.x + 12,
        enemy_panel.y + 60,
        enemy_creature.hp,
        enemy_creature.max_hp,
        width=140,
        height=14
    )

    # HP text (right of bar)
    draw_stat_text(
        game_surface,
        stat_font,
        f"{enemy_creature.hp}/{enemy_creature.max_hp}",
        enemy_panel.x + 160,
        enemy_panel.y + 58
    )

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
        draw_flamethrower(game_surface, start_x, start_y, end_x, end_y, progress)

    if move_effect == "thunderbolt" and move_effect_timer > 0:
        start_x = player_x_pos + 70
        start_y = player_y_pos + 35
        end_x = enemy_x + 30
        end_y = enemy_y + 35
        draw_thunderbolt(game_surface, start_x, start_y, end_x, end_y)

    player_panel = draw_info_panel(game_surface, 48, 198, 235, 100, (135, 206, 235))

    # Name
    draw_stat_text(
        game_surface,
        name_font,
        player_creature.name,
        player_panel.x + 12,
        player_panel.y + 10
    )

    # Type badge
    draw_type_badge(
        game_surface,
        player_creature.creature_type,
        player_panel.x + 170,
        player_panel.y + 10
    )

    # HP bar
    draw_hp_bar(
        player_panel.x + 12,
        player_panel.y + 60,
        player_creature.hp,
        player_creature.max_hp,
        width=140,
        height=14
    )

    # HP text
    draw_stat_text(
        game_surface,
        stat_font,
        f"{player_creature.hp}/{player_creature.max_hp}",
        player_panel.x + 160,
        player_panel.y + 58
    )

    pygame.draw.rect(game_surface, BOX_COLOR, (40, 430, 720, 130))
    pygame.draw.rect(game_surface, BLACK, (40, 430, 720, 130), 2)

    if battle_phase == "message":
        draw_text(current_battle_message, 60, 455)
        if pygame.time.get_ticks() // 300 % 2 == 0:
            draw_text("v", 720, 505)

    elif battle_phase == "action_menu":
        positions = [(70, 455), (380, 455), (70, 500), (380, 500)]

        for i, option in enumerate(battle_menu_options):
            prefix = ">" if i == battle_menu_index else " "
            x, y = positions[i]
            draw_text(f"{prefix} {option}", x, y)

    elif battle_phase == "move_menu":
        positions = [(70, 455), (380, 455), (70, 500), (380, 500)]

        for i, move in enumerate(player_creature.moves):
            prefix = ">" if i == move_menu_index else " "
            x, y = positions[i]
            draw_text(f"{prefix} {move.name}", x, y)


def enemy_turn(
    enemy_creature,
    player_creature,
    battle_result_timer,
):
    move = random.choice(enemy_creature.moves)
    damage, multiplier = calculate_move_damage(enemy_creature, player_creature, move)
    player_creature.hp = max(0, player_creature.hp - damage)

    attack_attacker = "enemy"
    attack_timer = 10

    hit_target = "player"
    hit_timer = 12

    battle_message = f"{enemy_creature.name} used {move.name}!"

    if multiplier > 1.0:
        battle_message += " It's super effective!"
    elif multiplier < 1.0:
        battle_message += " It's not very effective..."

    move_effect = move.animation
    move_effect_timer = 18 if move.animation == "flamethrower" else 8 if move.animation == "thunderbolt" else 0

    game_state = None

    if player_creature.is_fainted():
        battle_message = f"{player_creature.name} fainted! You lost!"
        game_state = "battle_end"
        battle_result_timer = 120

    return {
        "battle_message": battle_message,
        "game_state": game_state,
        "battle_result_timer": battle_result_timer,
        "hit_target": hit_target,
        "hit_timer": hit_timer,
        "attack_attacker": attack_attacker,
        "attack_timer": attack_timer,
        "move_effect": move_effect,
        "move_effect_timer": move_effect_timer,
    }