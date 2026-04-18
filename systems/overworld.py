from settings import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

def get_tile_at_pixel(x, y, game_map):
    col = x // TILE_SIZE
    row = y // TILE_SIZE

    if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
        return game_map[row][col]

    return "#"


def can_move_to(x, y, player_size, game_map):
    corners = [
        (x, y),
        (x + player_size, y),
        (x, y + player_size),
        (x + player_size, y + player_size)
    ]

    for corner_x, corner_y in corners:
        tile = get_tile_at_pixel(corner_x, corner_y, game_map)
        if tile == "#":
            return False

    return True


def player_is_in_tall_grass(player_x, player_y, player_size, game_map):
    center_x = player_x + player_size // 2
    center_y = player_y + player_size // 2
    tile = get_tile_at_pixel(center_x, center_y, game_map)
    return tile == "G"


def draw_map(game_surface, game_map, ground_tile, tall_grass_tile, wall_tile):
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


def draw_player(
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
):
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