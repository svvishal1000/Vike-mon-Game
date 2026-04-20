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

    draw_text(enemy_creature.name, 470, 80)
    draw_text(f"HP: {enemy_creature.hp}/{enemy_creature.max_hp}", 470, 110)
    draw_hp_bar(470, 140, enemy_creature.hp, enemy_creature.max_hp)

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

    draw_text(player_creature.name, 70, 210)
    draw_text(f"HP: {player_creature.hp}/{player_creature.max_hp}", 70, 240)
    draw_hp_bar(70, 270, player_creature.hp, player_creature.max_hp)

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