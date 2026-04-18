"""UI widgets and shared drawing helpers."""

import pygame

from snake_app.constants import BUTTON_COLOR, BUTTON_HOVER, HEIGHT, TEXT_COLOR, WIDTH


def draw_modern_background(surface):
    """Draw the menu and gameplay gradient background."""
    top_color = (30, 30, 60)
    bottom_color = (10, 10, 40)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        red = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        green = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        blue = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (red, green, blue), (0, y), (WIDTH, y))


def draw_text(surface, text, size, color, x, y):
    """Render centered text on the target surface."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


class Button:
    """Interactive menu button with hover scaling."""

    def __init__(self, x, y, width, height, text, callback):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.callback = callback
        self.hovered = False
        self.current_scale = 1.0

    def draw(self, surface):
        """Draw button state on screen."""
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
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Slider:
    """Simple horizontal slider for settings values."""

    def __init__(self, x, y, width, value=0.5, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.value = value
        self.label = label
        self.dragging = False

    def draw(self, surface):
        """Draw slider line, knob, and label."""
        pygame.draw.line(surface, (150, 150, 150), (self.x, self.y), (self.x + self.width, self.y), 4)
        knob_x = self.x + int(self.value * self.width)
        pygame.draw.circle(surface, (200, 200, 200), (knob_x, self.y), 10)
        font = pygame.font.Font(None, 24)
        label_text = f"{self.label}: {int(self.value * 100)}%"
        text_surface = font.render(label_text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midtop=(self.x + self.width / 2, self.y + 20))
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Update slider state while dragging the knob."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            knob_x = self.x + int(self.value * self.width)
            if (mouse_x - knob_x) ** 2 + (mouse_y - self.y) ** 2 <= 10 ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, _ = event.pos
            self.value = max(0.0, min(1.0, (mouse_x - self.x) / self.width))
