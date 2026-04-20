import cv2
import math
import pygame
import sys

from settings import WIDTH, HEIGHT, WHITE, BLACK, BOX_COLOR
from utils.helpers import load_sprite

def play_intro_video(screen, game_surface, pygame_mixer, clock):
    cap = cv2.VideoCapture("intro.mp4")

    if not cap.isOpened():
        print("Error: Could not open video")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_delay = int(1000 / fps)

    try:
        pygame_mixer.music.load("intro.mp3")
        pygame_mixer.music.play()
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

        screen_width, screen_height = screen.get_size()

        scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))

        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    cap.release()
                    pygame_mixer.music.stop()
                    return
            elif event.type == pygame.QUIT:
                cap.release()
                pygame_mixer.music.stop()
                pygame.quit()
                sys.exit()

        pygame.time.wait(frame_delay)

    cap.release()
    pygame_mixer.music.stop()

def play_welcome_video(screen, game_surface, font):
    cap = cv2.VideoCapture("welcome.mp4")

    if not cap.isOpened():
        print("Error: Could not open welcome.mp4")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_delay = int(1000 / fps)

    last_frame_surface = None

    # First: play the video once
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        last_frame_surface = pygame_frame.copy()

        game_surface.blit(pygame_frame, (0, 0))

        screen_width, screen_height = screen.get_size()

        scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))

        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()

        pygame.time.wait(frame_delay)

    cap.release()

    if last_frame_surface is None:
        return

    # Then: hold last frame and show dialogue box until Enter
    full_text = "Welcome to Vike'Mon World!"
    displayed_length = 0
    text_timer = 0
    arrow_timer = 0

    while True:
        arrow_timer += 1
        text_timer += 1

        if displayed_length < len(full_text) and text_timer % 3 == 0:
            displayed_length += 1

        current_text = full_text[:displayed_length]

        game_surface.blit(last_frame_surface, (0, 0))

        # Dialogue box drawn directly on screen (not game_surface)
        pygame.draw.rect(screen, BOX_COLOR, (40, 430, 720, 130))
        pygame.draw.rect(screen, BLACK, (40, 430, 720, 130), 2)

        dialogue_text = font.render(current_text, True, BLACK)
        screen.blit(dialogue_text, (70, 465))

        # Arrow appears only after full text
        if displayed_length == len(full_text):
            if (arrow_timer // 20) % 2 == 0:
                arrow_text = font.render("v", True, BLACK)
                screen.blit(arrow_text, (720, 505))

            screen_width, screen_height = screen.get_size()

            scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))

            screen.blit(scaled_surface, (0, 0))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

            pygame.time.delay(30)


def play_title_menu(
    screen,
    game_surface,
    pygame_mixer,
    clock,
    title_logo,
    font,
    options,
    menu_move_sound,
    menu_select_sound,
):
    cap = cv2.VideoCapture("title_menu.mp4")

    if not cap.isOpened():
        print("Error: Could not open title_menu.mp4")
        return "new_game"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_delay = int(1000 / fps)

    try:
        pygame_mixer.music.load("title_menu.mp3")
        pygame_mixer.music.play(-1)
    except:
        print("Warning: Could not load title_menu.mp3")

    selected_option = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        game_surface.blit(pygame_frame, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        game_surface.blit(overlay, (0, 0))

        logo_y = 80 + int(math.sin(pygame.time.get_ticks() * 0.002) * 5)
        scale = 1 + (math.sin(pygame.time.get_ticks() * 0.003) * 0.02)

        scaled_logo = pygame.transform.scale(
            title_logo,
            (int(420 * scale), int(140 * scale))
        )

        scaled_x = 80
        game_surface.blit(scaled_logo, (scaled_x, logo_y))

        if int(pygame.time.get_ticks() * 0.01) % 40 == 0:
            sparkle_x = scaled_x + scaled_logo.get_width() - 30
            sparkle_y = logo_y + 18
            pygame.draw.circle(game_surface, (255, 255, 255), (sparkle_x, sparkle_y), 3)
            pygame.draw.circle(game_surface, (255, 255, 180), (sparkle_x, sparkle_y), 6, 1)

        menu_x = 520
        start_y = 260
        line_spacing = 60

        for i, option in enumerate(options):
            y = start_y + i * line_spacing

            if i == selected_option:
                pulse = int(55 * (math.sin(pygame.time.get_ticks() * 0.005) + 1))
                color = (255, 255, 200 + pulse // 2)

                scale = 1 + (math.sin(pygame.time.get_ticks() * 0.005) * 0.05)

                option_surface = font.render(option, True, color)
                scaled_option = pygame.transform.scale(
                    option_surface,
                    (
                        int(option_surface.get_width() * scale),
                        int(option_surface.get_height() * scale)
                    )
                )

                draw_x = menu_x
                draw_y = y - (scaled_option.get_height() - option_surface.get_height()) // 2

                arrow_icon = load_sprite("arrow.png", 24, 24)
                game_surface.blit(arrow_icon, (menu_x - 40, y + 5))
                game_surface.blit(scaled_option, (draw_x, draw_y))
            else:
                color = (200, 200, 200)
                option_text = font.render(option, True, color)
                game_surface.blit(option_text, (menu_x, y))

        hint_text = font.render("Use UP/DOWN and ENTER", True, WHITE)
        game_surface.blit(hint_text, (470, 500))

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
                pygame_mixer.music.stop()
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

                    pygame.time.delay(150)

                    cap.release()
                    pygame_mixer.music.stop()

                    if selected_option == 0:
                        return "new_game"
                    elif selected_option == 1:
                        return "continue"
                    else:
                        pygame.quit()
                        sys.exit()

                elif event.key == pygame.K_ESCAPE:
                    cap.release()
                    pygame_mixer.music.stop()
                    pygame.quit()
                    sys.exit()

        pygame.time.wait(frame_delay)