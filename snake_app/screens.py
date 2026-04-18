"""Standalone menu and dialog screens."""

import sys

import pygame

from snake_app.constants import ASSETS_DIR, HEIGHT, TEXT_COLOR, WIDTH
from snake_app.models import Leaderboard
from snake_app.settings import save_settings, set_game_speed, set_sound_volume
import snake_app.settings as settings
from snake_app.ui import Button, Slider, draw_modern_background, draw_text


def countdown(screen):
    """Display countdown before gameplay starts or resumes."""
    clock = pygame.time.Clock()
    countdown_sound = pygame.mixer.Sound(str(ASSETS_DIR / "countdown.wav"))
    countdown_sound.set_volume(settings.sound_volume)
    countdown_sound.play()

    start_time = pygame.time.get_ticks()
    duration = 3000
    go_displayed = False

    while True:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        draw_modern_background(screen)

        if elapsed < duration:
            seconds_left = 3 - int(elapsed / 1000)
            draw_text(screen, str(seconds_left), 100, TEXT_COLOR, WIDTH // 2, HEIGHT // 2)
        elif not go_displayed:
            draw_text(screen, "Go!", 100, TEXT_COLOR, WIDTH // 2, HEIGHT // 2)
            go_displayed = True
            go_start = pygame.time.get_ticks()
        else:
            if pygame.time.get_ticks() - go_start >= 1000:
                return
            draw_text(screen, "Go!", 100, TEXT_COLOR, WIDTH // 2, HEIGHT // 2)

        pygame.display.flip()
        clock.tick(30)


def username_input(screen):
    """Collect username before starting gameplay."""
    clock = pygame.time.Clock()
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 60)
    base_color = pygame.Color("lightskyblue3")
    active_color = pygame.Color("dodgerblue2")
    color = base_color
    active = False
    text = ""
    font = pygame.font.Font(None, 48)
    placeholder = "Enter your username"
    blink_time = 0
    cursor_visible = True

    back_button = Button(WIDTH // 2 - 50, HEIGHT - 80, 100, 50, "Back", lambda: "back")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.rect.collidepoint(event.pos):
                    return "back"
                active = input_box.collidepoint(event.pos)
                color = active_color if active else base_color
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    return text.strip() if text.strip() else "Player"
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        blink_time += clock.get_time()
        if blink_time > 500:
            blink_time = 0
            cursor_visible = not cursor_visible

        draw_modern_background(screen)
        draw_text(screen, "Welcome", 60, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 100)

        if text == "" and not active:
            text_surface = font.render(placeholder, True, (180, 180, 180))
        else:
            text_surface = font.render(text, True, TEXT_COLOR)

        input_box.w = max(300, text_surface.get_width() + 20)
        pygame.draw.rect(screen, (50, 50, 50), input_box, border_radius=10)
        pygame.draw.rect(screen, color, input_box, 2, border_radius=10)
        screen.blit(
            text_surface,
            (input_box.x + 10, input_box.y + (input_box.height - text_surface.get_height()) / 2),
        )

        if active and cursor_visible:
            cursor_x = input_box.x + 10 + text_surface.get_width() + 2
            pygame.draw.line(
                screen,
                TEXT_COLOR,
                (cursor_x, input_box.y + 10),
                (cursor_x, input_box.y + input_box.height - 10),
                2,
            )

        instruction_surface = pygame.font.Font(None, 32).render(
            "Press ENTER to continue",
            True,
            TEXT_COLOR,
        )
        screen.blit(
            instruction_surface,
            (WIDTH // 2 - instruction_surface.get_width() // 2, input_box.y + input_box.height + 20),
        )

        mouse_pos = pygame.mouse.get_pos()
        back_button.hovered = back_button.rect.collidepoint(mouse_pos)
        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(30)


def settings_menu(screen):
    """Display sliders for volume and speed settings."""
    clock = pygame.time.Clock()
    slider_width = 300
    slider_sound = Slider(
        WIDTH // 2 - slider_width // 2,
        200,
        slider_width,
        value=settings.sound_volume,
        label="Sound Volume",
    )
    slider_speed = Slider(
        WIDTH // 2 - slider_width // 2,
        300,
        slider_width,
        value=settings.game_speed,
        label="Game Speed",
    )
    back_button = Button(WIDTH // 2 - 100, 400, 200, 50, "Back", lambda: "back")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            slider_sound.handle_event(event)
            slider_speed.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.rect.collidepoint(event.pos):
                return

        set_sound_volume(slider_sound.value)
        set_game_speed(slider_speed.value)
        pygame.mixer.music.set_volume(settings.sound_volume)
        save_settings()

        draw_modern_background(screen)
        draw_text(screen, "Settings", 64, TEXT_COLOR, WIDTH // 2, 100)
        slider_sound.draw(screen)
        slider_speed.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        back_button.hovered = back_button.rect.collidepoint(mouse_pos)
        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(30)


def show_leaderboard(screen):
    """Display persisted leaderboard scores."""
    leaderboard = Leaderboard()
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", lambda: None)

    button_font = pygame.font.Font(None, 36)
    clear_text_surface = button_font.render("Clear Leaderboard", True, TEXT_COLOR)
    clear_button = Button(
        WIDTH // 2 - (clear_text_surface.get_width() + 20) // 2,
        HEIGHT - 140,
        clear_text_surface.get_width() + 20,
        50,
        "Clear Leaderboard",
        lambda: "clear",
    )

    while True:
        draw_modern_background(screen)
        draw_text(screen, "Leaderboard", 64, TEXT_COLOR, WIDTH // 2, 50)

        y = 120
        for index, entry in enumerate(leaderboard.scores[:10]):
            line = f"{index + 1}. {entry['username']} - {entry['score']} ({entry['date']})"
            draw_text(screen, line, 32, TEXT_COLOR, WIDTH // 2, y)
            y += 50

        mouse_pos = pygame.mouse.get_pos()
        clear_button.hovered = clear_button.rect.collidepoint(mouse_pos)
        back_button.hovered = back_button.rect.collidepoint(mouse_pos)
        clear_button.draw(screen)
        back_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clear_button.rect.collidepoint(event.pos):
                    leaderboard.scores = []
                    leaderboard.save()
                elif back_button.rect.collidepoint(event.pos):
                    return


def game_over_screen(screen, score, username):
    """Show game-over choices and return selected action."""
    _ = username
    main_menu_button = Button(170, HEIGHT // 2 + 50, 140, 50, "Main Menu", lambda: "main_menu")
    restart_button = Button(330, HEIGHT // 2 + 50, 140, 50, "Restart", lambda: "restart")
    exit_button = Button(490, HEIGHT // 2 + 50, 140, 50, "Exit", lambda: "exit")

    while True:
        draw_modern_background(screen)
        draw_text(screen, "Game Over", 64, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 100)
        draw_text(screen, f"Score: {score}", 48, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 30)
        mouse_pos = pygame.mouse.get_pos()
        for button in (main_menu_button, restart_button, exit_button):
            button.hovered = button.rect.collidepoint(mouse_pos)
            button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if main_menu_button.rect.collidepoint(event.pos):
                    return "main_menu"
                if restart_button.rect.collidepoint(event.pos):
                    return "restart"
                if exit_button.rect.collidepoint(event.pos):
                    return "exit"


def pause_menu(screen):
    """Show paused overlay and return resume or menu choice."""
    resume_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Resume", lambda: "resume")
    menu_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Main Menu", lambda: "menu")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_SPACE):
                return "resume"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.rect.collidepoint(event.pos):
                    return "resume"
                if menu_button.rect.collidepoint(event.pos):
                    return "menu"

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "PAUSED", 100, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 150)
        mouse_pos = pygame.mouse.get_pos()
        resume_button.hovered = resume_button.rect.collidepoint(mouse_pos)
        menu_button.hovered = menu_button.rect.collidepoint(mouse_pos)
        resume_button.draw(screen)
        menu_button.draw(screen)
        pygame.display.flip()


def how_to_play_screen(screen):
    """Display static gameplay instructions."""
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", lambda: None)
    instructions = [
        "Objective:",
        "- Eat the food to grow your snake.",
        "- Avoid hitting the walls or yourself.",
        "",
        "Controls:",
        "- Use ARROW KEYS to move the snake.",
        "- Press P to pause/unpause the game.",
        "",
        "Rules:",
        "- Each food eaten increases your score by 10.",
        "- The game ends if you hit a wall or yourself.",
        "- Special food spawns every 4 seconds and is worth double the points.",
        "",
        "Tips:",
        "- Plan your moves to avoid trapping yourself.",
        "- The snake moves faster as you progress.",
    ]

    base_font_size = max(24, int(HEIGHT / 25))
    line_spacing = int(base_font_size * 1.2)
    start_y = (HEIGHT - len(instructions) * line_spacing) // 2

    while True:
        draw_modern_background(screen)
        draw_text(
            screen,
            "How to Play",
            int(base_font_size * 1.5),
            TEXT_COLOR,
            WIDTH // 2,
            start_y - line_spacing - 10,
        )

        y = start_y
        for line in instructions:
            draw_text(screen, line, base_font_size, TEXT_COLOR, WIDTH // 2, y)
            y += line_spacing

        mouse_pos = pygame.mouse.get_pos()
        back_button.hovered = back_button.rect.collidepoint(mouse_pos)
        back_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.rect.collidepoint(event.pos):
                return
