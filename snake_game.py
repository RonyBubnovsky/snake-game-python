# Import necessary libraries
import pygame
import random
import sys
import json
from datetime import datetime
import os

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH, HEIGHT = 800, 600  # Screen dimensions
GRID_SIZE = 20  # Size of each grid cell

# Global settings
sound_volume = 0.5  # Default sound volume
game_speed = 0.1  # Default game speed

# Colors
BUTTON_COLOR = (50, 50, 70)  # Default button color
BUTTON_HOVER = (70, 70, 90)  # Button color when hovered
TEXT_COLOR = (200, 200, 210)  # Text color
FOOD_COLOR = (255, 50, 75)  # Food color

# File paths
LEADERBOARD_FILE = "leaderboard.json"  # Leaderboard file
SETTINGS_FILE = "settings.json"  # Settings file

def load_settings():
    """Load game settings from a file."""
    global sound_volume, game_speed
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                sound_volume = settings.get("sound_volume", 0.5)
                game_speed = settings.get("game_speed", 0.4)
        except Exception as e:
            print("Error loading settings:", e)
    else:
        sound_volume = 0.5
        game_speed = 0.1

def save_settings():
    """Save game settings to a file."""
    settings = {
        "sound_volume": sound_volume,
        "game_speed": game_speed
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        print("Error saving settings:", e)

# Load settings at the start
load_settings()

def draw_modern_background(surface):
    """Draw a gradient background."""
    top_color = (30, 30, 60)  # Top color of the gradient
    bottom_color = (10, 10, 40)  # Bottom color of the gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

class Button:
    """A class to create interactive buttons."""
    def __init__(self, x, y, width, height, text, callback):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.callback = callback
        self.hovered = False
        self.current_scale = 1.0

    def draw(self, surface):
        """Draw the button on the screen."""
        target_scale = 1.1 if self.hovered else 1.0
        self.current_scale += (target_scale - self.current_scale) * 0.2
        new_width = self.original_rect.width * self.current_scale
        new_height = self.original_rect.height * self.current_scale
        new_x = self.original_rect.centerx - new_width / 2
        new_y = self.original_rect.centery - new_height / 2
        self.rect = pygame.Rect(new_x, new_y, new_width, new_height)
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Slider:
    """A class to create interactive sliders."""
    def __init__(self, x, y, width, value=0.5, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.value = value
        self.label = label
        self.dragging = False

    def draw(self, surface):
        """Draw the slider on the screen."""
        slider_line_color = (150, 150, 150)
        slider_line_thickness = 4
        pygame.draw.line(surface, slider_line_color, (self.x, self.y), (self.x + self.width, self.y), slider_line_thickness)
        knob_radius = 10
        knob_x = self.x + int(self.value * self.width)
        knob_y = self.y
        knob_color = (200, 200, 200)
        pygame.draw.circle(surface, knob_color, (knob_x, knob_y), knob_radius)
        font = pygame.font.Font(None, 24)
        label_text = f"{self.label}: {int(self.value * 100)}%"
        text_surf = font.render(label_text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(midtop=(self.x + self.width / 2, self.y + 20))
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Handle slider events (e.g., dragging)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            knob_radius = 10
            knob_x = self.x + int(self.value * self.width)
            knob_y = self.y
            if (mouse_x - knob_x) ** 2 + (mouse_y - knob_y) ** 2 <= knob_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                self.value = max(0.0, min(1.0, (mouse_x - self.x) / self.width))

class Leaderboard:
    """A class to manage the leaderboard."""
    def __init__(self):
        self.scores = []
        self.load()
    
    def load(self):
        """Load the leaderboard from a file."""
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                self.scores = json.load(f)
        except FileNotFoundError:
            self.scores = []
    
    def save(self):
        """Save the leaderboard to a file."""
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, username, score):
        """Add a new score to the leaderboard."""
        existing = next((s for s in self.scores if s["username"].lower() == username.lower()), None)
        if existing:
            if score > existing["score"]:
                existing["score"] = score
                existing["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            self.scores.append({
                "username": username,
                "score": score,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]
        self.save()

class Snake:
    """A class to represent the snake."""
    def __init__(self):
        self.head = [WIDTH // 2, HEIGHT // 2]  # Initial position of the snake head
        self.body = []  # List to store body segments
        self.direction = "RIGHT"  # Initial direction
        self.new_direction = "RIGHT"  # New direction (to handle input)
        self.grow = False  # Whether the snake should grow

    def move(self):
        """Move the snake based on its direction."""
        if self.new_direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
        if self.new_direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        if self.new_direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        if self.new_direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"

        # Always insert the current head position into the body
        self.body.insert(0, self.head.copy())
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

        # Move the head
        if self.direction == "RIGHT":
            self.head[0] += GRID_SIZE
        elif self.direction == "LEFT":
            self.head[0] -= GRID_SIZE
        elif self.direction == "UP":
            self.head[1] -= GRID_SIZE
        elif self.direction == "DOWN":
            self.head[1] += GRID_SIZE

class Food:
    """A class to represent the normal food."""
    def __init__(self):
        self.position = [0, 0]  # Initial position of the food
        self.spawn()
        self.particles = []  # Particles for visual effect
    
    def spawn(self):
        """Spawn food at a random position, avoiding the pause and score areas."""
        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        while True:
            x = random.randrange(0, WIDTH, GRID_SIZE)
            y = random.randrange(0, HEIGHT, GRID_SIZE)
            food_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if food_rect.colliderect(forbidden_pause) or food_rect.colliderect(forbidden_score):
                continue
            else:
                self.position = [x, y]
                break
    
    def create_particles(self):
        """Create particles when the food is eaten."""
        for _ in range(10):
            self.particles.append([
                self.position[0] + GRID_SIZE // 2,
                self.position[1] + GRID_SIZE // 2,
                random.uniform(-2, 2),
                random.uniform(-2, 2),
                random.randint(3, 6)
            ])
    
    def update_particles(self):
        """Update particles."""
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.1
            if p[4] <= 0:
                self.particles.remove(p)

class SpecialFood:
    """A class to represent the special double food.
       Spawns as two images side by side,
       moves randomly faster than normal food, is worth double the points (20 points),
       and shows particle effects when eaten.
       After being eaten, a new special food will spawn after 4 seconds."""
    def __init__(self, food_image):
        self.food_image1 = food_image.copy()
        self.food_image2 = food_image.copy()
        self.food_image1.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
        self.food_image2.fill((255, 255, 0), special_flags=pygame.BLEND_MULT)  
        self.spawn()
        # Increase speed for special food: using values -3, -2, 2, or 3
        self.dx = random.choice([-5, -4, 4, 5])
        self.dy = random.choice([-5, -4, 4, 5])
        self.points = 20
        self.particles = []

    def spawn(self):
        """Spawn special food at a random position, avoiding the pause and score areas.
           The special food occupies 2*GRID_SIZE in width."""
        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        while True:
            x = random.randrange(0, WIDTH - 2 * GRID_SIZE, GRID_SIZE)
            y = random.randrange(0, HEIGHT - GRID_SIZE, GRID_SIZE)
            special_rect = pygame.Rect(x, y, 2 * GRID_SIZE, GRID_SIZE)
            if special_rect.colliderect(forbidden_pause) or special_rect.colliderect(forbidden_score):
                continue
            else:
                self.x = x
                self.y = y
                break

    def update(self):
        """Update the special food's position and bounce off boundaries or forbidden areas."""
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH - 2 * GRID_SIZE:
            self.dx = -self.dx
            self.x += self.dx
        if self.y < 0 or self.y > HEIGHT - GRID_SIZE:
            self.dy = -self.dy
            self.y += self.dy
        special_rect = self.get_rect()
        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        if special_rect.colliderect(forbidden_pause) or special_rect.colliderect(forbidden_score):
            self.dx = -self.dx
            self.dy = -self.dy
            self.x += self.dx
            self.y += self.dy

    def draw(self, surface):
        """Draw the two food images side by side."""
        surface.blit(self.food_image1, (self.x, self.y))
        surface.blit(self.food_image2, (self.x + GRID_SIZE, self.y))

    def get_rect(self):
        """Return a Rect representing the special food's area."""
        return pygame.Rect(self.x, self.y, 2 * GRID_SIZE, GRID_SIZE)

    def create_particles(self):
        """Create particle effects for special food."""
        for _ in range(10):
            self.particles.append([
                self.x + GRID_SIZE, self.y + GRID_SIZE // 2,
                random.uniform(-2, 2), random.uniform(-2, 2),
                random.randint(3, 6)
            ])

    def update_particles(self):
        """Update special food particles."""
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.1
            if p[4] <= 0:
                self.particles.remove(p)

    def draw_particles(self, surface):
        """Draw special food particles."""
        for p in self.particles:
            pygame.draw.circle(surface, FOOD_COLOR, (int(p[0]), int(p[1])), int(p[4]))

def draw_text(surface, text, size, color, x, y):
    """Draw text on the screen."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def countdown(screen):
    """Display a countdown before starting/resuming the game."""
    clock = pygame.time.Clock()
    countdown_sound = pygame.mixer.Sound("assets/countdown.wav")
    countdown_sound.set_volume(sound_volume)
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
                break
            else:
                draw_text(screen, "Go!", 100, TEXT_COLOR, WIDTH // 2, HEIGHT // 2)

        pygame.display.flip()
        clock.tick(30)

def username_input(screen):
    """Allow the player to enter their username."""
    clock = pygame.time.Clock()
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 60)
    base_color = pygame.Color("lightskyblue3")
    active_color = pygame.Color("dodgerblue2")
    color = base_color
    active = False
    text = ""
    done = False
    font = pygame.font.Font(None, 48)
    placeholder = "Enter your username"
    blink_time = 0
    cursor_visible = True

    back_button = Button(WIDTH // 2 - 50, HEIGHT - 80, 100, 50, "Back", lambda: "back")
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.rect.collidepoint(event.pos):
                    return "back"
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = active_color if active else base_color
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
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
            txt_surface = font.render(placeholder, True, (180, 180, 180))
        else:
            txt_surface = font.render(text, True, TEXT_COLOR)

        width = max(300, txt_surface.get_width() + 20)
        input_box.w = width

        pygame.draw.rect(screen, (50, 50, 50), input_box, border_radius=10)
        pygame.draw.rect(screen, color, input_box, 2, border_radius=10)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + (input_box.height - txt_surface.get_height()) / 2))
        if active and cursor_visible:
            cursor_x = input_box.x + 10 + txt_surface.get_width() + 2
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, input_box.y + 10),
                             (cursor_x, input_box.y + input_box.height - 10), 2)

        instruction_text = "Press ENTER to continue"
        instruction_surface = pygame.font.Font(None, 32).render(instruction_text, True, TEXT_COLOR)
        screen.blit(instruction_surface, (WIDTH // 2 - instruction_surface.get_width() // 2,
                                          input_box.y + input_box.height + 20))
        mouse_pos = pygame.mouse.get_pos()
        back_button.hovered = back_button.rect.collidepoint(mouse_pos)
        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    return text.strip() if text.strip() != "" else "Player"

def settings_menu(screen):
    """Display the settings menu."""
    global sound_volume, game_speed
    clock = pygame.time.Clock()
    slider_width = 300
    slider_sound = Slider(WIDTH // 2 - slider_width // 2, 200, slider_width, value=sound_volume, label="Sound Volume")
    slider_speed = Slider(WIDTH // 2 - slider_width // 2, 300, slider_width, value=game_speed, label="Game Speed")
    back_button = Button(WIDTH // 2 - 100, 400, 200, 50, "Back", lambda: "back")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            slider_sound.handle_event(event)
            slider_speed.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.rect.collidepoint(event.pos):
                    running = False

        sound_volume = slider_sound.value
        game_speed = slider_speed.value
        pygame.mixer.music.set_volume(sound_volume)
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
    """Display the leaderboard."""
    leaderboard = Leaderboard()
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back", lambda: None)
    
    button_font = pygame.font.Font(None, 36)
    clear_text = "Clear Leaderboard"
    clear_text_surf = button_font.render(clear_text, True, TEXT_COLOR)
    clear_button_width = clear_text_surf.get_width() + 20
    clear_button = Button(WIDTH // 2 - clear_button_width // 2, HEIGHT - 140, clear_button_width, 50, clear_text, lambda: "clear")
    
    while True:
        draw_modern_background(screen)
        draw_text(screen, "Leaderboard", 64, TEXT_COLOR, WIDTH // 2, 50)
        
        y = 120
        for i, entry in enumerate(leaderboard.scores[:10]):
            text = f"{i+1}. {entry['username']} - {entry['score']} ({entry['date']})"
            draw_text(screen, text, 32, TEXT_COLOR, WIDTH // 2, y)
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
    """Display the game over screen."""
    main_menu_button = Button(170, HEIGHT // 2 + 50, 140, 50, "Main Menu", lambda: "main_menu")
    restart_button   = Button(330, HEIGHT // 2 + 50, 140, 50, "Restart",   lambda: "restart")
    exit_button      = Button(490, HEIGHT // 2 + 50, 140, 50, "Exit",      lambda: "exit")
    
    while True:
        draw_modern_background(screen)
        draw_text(screen, "Game Over", 64, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 100)
        draw_text(screen, f"Score: {score}", 48, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 30)
        mouse_pos = pygame.mouse.get_pos()
        for button in [main_menu_button, restart_button, exit_button]:
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
                elif restart_button.rect.collidepoint(event.pos):
                    return "restart"
                elif exit_button.rect.collidepoint(event.pos):
                    return "exit"

def pause_menu(screen):
    """Display the pause menu with options to resume or return to main menu.
       Also allows toggling pause by pressing P."""
    resume_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Resume", lambda: "resume")
    menu_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Main Menu", lambda: "menu")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return "resume"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.rect.collidepoint(event.pos):
                    return "resume"
                if menu_button.rect.collidepoint(event.pos):
                    return "menu"
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        draw_text(screen, "PAUSED", 100, TEXT_COLOR, WIDTH//2, HEIGHT//2 - 150)
        mouse_pos = pygame.mouse.get_pos()
        resume_button.hovered = resume_button.rect.collidepoint(mouse_pos)
        menu_button.hovered = menu_button.rect.collidepoint(mouse_pos)
        resume_button.draw(screen)
        menu_button.draw(screen)
        pygame.display.flip()

def how_to_play_screen(screen):
    """Display the 'How to Play' instructions."""
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
    "- The snake moves faster as you progress."
]

    
    base_font_size = max(24, int(HEIGHT / 25))
    line_spacing = int(base_font_size * 1.2)
    font = pygame.font.Font(None, base_font_size)
    
    total_text_height = len(instructions) * line_spacing
    start_y = (HEIGHT - total_text_height) // 2
    
    while True:
        draw_modern_background(screen)
        draw_text(screen, "How to Play", int(base_font_size * 1.5), TEXT_COLOR, WIDTH // 2, start_y - line_spacing - 10)
        
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.rect.collidepoint(event.pos):
                    return

def main_menu():
    """Display the main menu."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game - Main Menu")
    
    pygame.mixer.music.load("assets/background.wav")
    pygame.mixer.music.set_volume(sound_volume)
    pygame.mixer.music.play(-1)
    
    buttons = [
        Button(WIDTH // 2 - 100, 180, 200, 50, "Start Game", lambda: "start"),
        Button(WIDTH // 2 - 100, 240, 200, 50, "Leaderboard", lambda: "leaderboard"),
        Button(WIDTH // 2 - 100, 300, 200, 50, "Settings", lambda: "settings"),
        Button(WIDTH // 2 - 100, 360, 200, 50, "How to Play", lambda: "how_to_play"),
        Button(WIDTH // 2 - 100, 420, 200, 50, "Quit", lambda: "quit")
    ]
    
    while True:
        draw_modern_background(screen)
        draw_text(screen, "Snake Game", 64, TEXT_COLOR, WIDTH // 2, 100)
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
    """Run the main game loop."""
    pygame.mixer.music.stop()
    
    # Load assets
    snake_head_image = pygame.image.load("assets/snake_head.png").convert_alpha()
    snake_head_image = pygame.transform.scale(snake_head_image, (GRID_SIZE, GRID_SIZE))
    snake_body_image = pygame.image.load("assets/snake_body.png").convert_alpha()
    snake_body_image = pygame.transform.scale(snake_body_image, (GRID_SIZE, GRID_SIZE))
    food_image = pygame.image.load("assets/food.png").convert_alpha()
    food_image = pygame.transform.scale(food_image, (GRID_SIZE, GRID_SIZE))
    pause_image = pygame.image.load("assets/pause.png").convert_alpha()
    pause_image = pygame.transform.scale(pause_image, (40, 40))
    
    # Sound effects
    eat_sound = pygame.mixer.Sound("assets/eat.wav")
    eat_sound.set_volume(sound_volume)
    fail_sound = pygame.mixer.Sound("assets/fail.wav")
    fail_sound.set_volume(sound_volume)
    
    countdown(pygame.display.get_surface())
    
    snake = Snake()
    food = Food()
    special_food = None
    special_spawn_timer = pygame.time.get_ticks()  # Timer for special food spawn
    special_particles = []
    score = 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    start_time = pygame.time.get_ticks()
    failed = False
    current_fps = int(10 + game_speed * 20)
    is_paused = False
    pause_button_rect = pygame.Rect(WIDTH - 60, 20, 40, 40)
    
    while True:
        current_time = pygame.time.get_ticks()
        # Spawn special food if not present and 4 seconds have passed since last spawn
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
                if event.key == pygame.K_p:
                    is_paused = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button_rect.collidepoint(event.pos):
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
        
        # Collision with normal food
        if head == food.position:
            snake.grow = True
            food.spawn()
            food.create_particles()
            score += 10
            eat_sound.play()
        
        # Collision with special food if exists
        if special_food is not None:
            special_rect = special_food.get_rect()
            head_rect = pygame.Rect(snake.head[0], snake.head[1], GRID_SIZE, GRID_SIZE)
            if head_rect.colliderect(special_rect):
                snake.grow = True
                score += special_food.points
                eat_sound.play()
                # Create particle effect for special food
                special_food.create_particles()
                special_particles = special_food.particles[:]
                special_food = None
                special_spawn_timer = current_time  # Reset spawn timer

        # Update special food particles if any
        if special_particles:
            for p in special_particles[:]:
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 0.1
                if p[4] <= 0:
                    special_particles.remove(p)
        
        # Check boundaries and self-collision
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
        # Draw normal food and its particles
        screen.blit(food_image, (food.position[0], food.position[1]))
        food.update_particles()
        for p in food.particles:
            pygame.draw.circle(screen, FOOD_COLOR, (int(p[0]), int(p[1])), int(p[4]))
        
        # Update and draw special food if exists
        if special_food is not None:
            special_food.update()
            special_food.draw(screen)
        # Draw special food particles if they exist
        if special_particles:
            for p in special_particles:
                pygame.draw.circle(screen, FOOD_COLOR, (int(p[0]), int(p[1])), int(p[4]))
        
        # Rotate the snake head image based on direction
        angle = 0
        if snake.direction == "UP":
            angle = 90
        elif snake.direction == "LEFT":
            angle = 180
        elif snake.direction == "DOWN":
            angle = -90
        rotated_head = pygame.transform.rotate(snake_head_image, angle)
        screen.blit(rotated_head, (snake.head[0], snake.head[1]))
        
        # Draw snake body
        for segment in snake.body:
            screen.blit(snake_body_image, (segment[0], segment[1]))
        
        # Draw UI elements
        screen.blit(pause_image, (WIDTH - 60, 20))
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(current_fps)
    
    Leaderboard().add_score(username, score)
    decision = game_over_screen(screen, score, username)
    if decision == "main_menu":
        main_menu()
    elif decision == "restart":
        run_game(username)
    elif decision == "exit":
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main_menu()
