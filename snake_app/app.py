"""Application bootstrap, menus, and main gameplay loop."""

import sys

import pygame

from snake_app.constants import ASSETS_DIR, FOOD_COLOR, GRID_SIZE, HEIGHT, TEXT_COLOR, WIDTH
from snake_app.models import Food, Leaderboard, Snake, SpecialFood
from snake_app.screens import (
    countdown,
    game_over_screen,
    how_to_play_screen,
    pause_menu,
    settings_menu,
    show_leaderboard,
    username_input,
)
import snake_app.settings as settings
from snake_app.ui import Button, draw_modern_background


pygame.init()
pygame.mixer.init()


def load_scaled_image(path, size):
    """Load an image asset and scale it to target size."""
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)


def load_game_assets():
    """Load all gameplay images and sounds."""
    snake_head_image = load_scaled_image(ASSETS_DIR / "snake_head.png", (GRID_SIZE, GRID_SIZE))
    snake_body_image = load_scaled_image(ASSETS_DIR / "snake_body.png", (GRID_SIZE, GRID_SIZE))
    food_image = load_scaled_image(ASSETS_DIR / "food.png", (GRID_SIZE, GRID_SIZE))
    pause_image = load_scaled_image(ASSETS_DIR / "pause.png", (40, 40))

    eat_sound = pygame.mixer.Sound(str(ASSETS_DIR / "eat.wav"))
    eat_sound.set_volume(settings.sound_volume)
    fail_sound = pygame.mixer.Sound(str(ASSETS_DIR / "fail.wav"))
    fail_sound.set_volume(settings.sound_volume)

    return snake_head_image, snake_body_image, food_image, pause_image, eat_sound, fail_sound


def update_special_particles(special_particles):
    """Advance and expire detached special food particles."""
    for particle in special_particles[:]:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[4] -= 0.1
        if particle[4] <= 0:
            special_particles.remove(particle)


def draw_food_particles(screen, particles):
    """Draw food burst particles."""
    for particle in particles:
        pygame.draw.circle(screen, FOOD_COLOR, (int(particle[0]), int(particle[1])), int(particle[4]))


def draw_snake(screen, snake, snake_head_image, snake_body_image):
    """Draw rotated snake head plus body segments."""
    angle = 0
    if snake.direction == "UP":
        angle = 90
    elif snake.direction == "LEFT":
        angle = 180
    elif snake.direction == "DOWN":
        angle = -90

    rotated_head = pygame.transform.rotate(snake_head_image, angle)
    screen.blit(rotated_head, (snake.head[0], snake.head[1]))
    for segment in snake.body:
        screen.blit(snake_body_image, (segment[0], segment[1]))


def handle_game_over(screen, score, username):
    """Store score, show decision screen, then route action."""
    Leaderboard().add_score(username, score)
    decision = game_over_screen(screen, score, username)
    if decision == "main_menu":
        main_menu()
    elif decision == "restart":
        run_game(username)
    elif decision == "exit":
        pygame.quit()
        sys.exit()


def main_menu():
    """Display main menu and route to selected screen."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game - Main Menu")

    pygame.mixer.music.load(str(ASSETS_DIR / "background.wav"))
    pygame.mixer.music.set_volume(settings.sound_volume)
    pygame.mixer.music.play(-1)

    buttons = [
        Button(WIDTH // 2 - 100, 180, 200, 50, "Start Game", lambda: "start"),
        Button(WIDTH // 2 - 100, 240, 200, 50, "Leaderboard", lambda: "leaderboard"),
        Button(WIDTH // 2 - 100, 300, 200, 50, "Settings", lambda: "settings"),
        Button(WIDTH // 2 - 100, 360, 200, 50, "How to Play", lambda: "how_to_play"),
        Button(WIDTH // 2 - 100, 420, 200, 50, "Quit", lambda: "quit"),
    ]

    while True:
        draw_modern_background(screen)
        font = pygame.font.Font(None, 64)
        title_surface = font.render("Snake Game", True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.hovered = button.rect.collidepoint(mouse_pos)
            button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        result = button.callback()
                        if result == "start":
                            username = username_input(screen)
                            if username == "back":
                                continue
                            run_game(username)
                        elif result == "leaderboard":
                            show_leaderboard(screen)
                        elif result == "settings":
                            settings_menu(screen)
                        elif result == "how_to_play":
                            how_to_play_screen(screen)
                        elif result == "quit":
                            pygame.quit()
                            sys.exit()


def run_game(username):
    """Run gameplay loop for one session."""
    pygame.mixer.music.stop()

    snake_head_image, snake_body_image, food_image, pause_image, eat_sound, fail_sound = load_game_assets()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    countdown(screen)

    snake = Snake()
    food = Food()
    special_food = None
    special_spawn_timer = pygame.time.get_ticks()
    special_particles = []
    score = 0
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    failed = False
    current_fps = int(10 + settings.game_speed * 20)
    is_paused = False
    pause_button_rect = pygame.Rect(WIDTH - 60, 20, 40, 40)

    while True:
        current_time = pygame.time.get_ticks()
        if special_food is None and current_time - special_spawn_timer >= 4000:
            special_food = SpecialFood(food_image)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not is_paused:
                    if event.key == pygame.K_RIGHT:
                        snake.new_direction = "RIGHT"
                    elif event.key == pygame.K_LEFT:
                        snake.new_direction = "LEFT"
                    elif event.key == pygame.K_UP:
                        snake.new_direction = "UP"
                    elif event.key == pygame.K_DOWN:
                        snake.new_direction = "DOWN"
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    is_paused = True
            if event.type == pygame.MOUSEBUTTONDOWN and pause_button_rect.collidepoint(event.pos):
                is_paused = True

        if is_paused:
            result = pause_menu(screen)
            if result == "resume":
                countdown(screen)
                is_paused = False
            elif result == "menu":
                main_menu()
                return

        snake.move()
        head = snake.head

        if head == food.position:
            snake.grow = True
            food.spawn()
            food.create_particles()
            score += 10
            eat_sound.play()

        if special_food is not None:
            head_rect = pygame.Rect(snake.head[0], snake.head[1], GRID_SIZE, GRID_SIZE)
            if head_rect.colliderect(special_food.get_rect()):
                snake.grow = True
                score += special_food.points
                eat_sound.play()
                special_food.create_particles()
                special_particles = special_food.particles[:]
                special_food = None
                special_spawn_timer = current_time

        if special_particles:
            update_special_particles(special_particles)

        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            if not failed:
                fail_sound.play()
                failed = True
            break
        if head in snake.body:
            if not failed:
                fail_sound.play()
                failed = True
            break

        draw_modern_background(screen)
        screen.blit(food_image, (food.position[0], food.position[1]))
        food.update_particles()
        draw_food_particles(screen, food.particles)

        if special_food is not None:
            special_food.update()
            special_food.draw(screen)
        if special_particles:
            draw_food_particles(screen, special_particles)

        draw_snake(screen, snake, snake_head_image, snake_body_image)
        screen.blit(pause_image, (WIDTH - 60, 20))
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()
        clock.tick(current_fps)

    handle_game_over(screen, score, username)
