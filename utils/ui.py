import pygame

from settings import WIDTH, HEIGHT, BLACK, WHITE

def draw_wrapped_text(screen, font, text, x, y, max_width, line_spacing=6):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    lines.append(current_line)

    for i, line in enumerate(lines):
        line_surface = font.render(line.strip(), True, (20, 20, 20))
        screen.blit(line_surface, (x, y + i * (font.get_height() + line_spacing)))


def draw_story_dialogue_box(screen, font, text, show_arrow=False):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Bigger centered box
    box_width = int(screen_width * 0.75)
    box_height = 200
    box_x = (screen_width - box_width) // 2
    box_y = screen_height - box_height - 40

    # Matte sky blue colors
    outer_color = (80, 150, 200)      # border (sky blue matte)
    inner_color = (210, 235, 255)     # soft light fill
    border_dark = (40, 90, 130)       # darker edge

    # Shadow (subtle)
    shadow = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 70))
    screen.blit(shadow, (box_x + 5, box_y + 5))

    # Outer box (solid matte)
    pygame.draw.rect(screen, outer_color, (box_x, box_y, box_width, box_height), border_radius=16)

    # Inner panel
    pygame.draw.rect(screen, inner_color,
                     (box_x + 6, box_y + 6, box_width - 12, box_height - 12),
                     border_radius=12)

    # Border outline
    pygame.draw.rect(screen, border_dark,
                     (box_x, box_y, box_width, box_height),
                     3, border_radius=16)

    draw_wrapped_text(
        screen,
        font,
        text,
        box_x + 30,
        box_y + 40,
        box_width - 80
    )

    # Arrow
    if show_arrow:
        arrow_surface = font.render("v", True, (20, 20, 20))
        screen.blit(arrow_surface, (box_x + box_width - 60, box_y + box_height - 55))