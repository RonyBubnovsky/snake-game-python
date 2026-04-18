"""Game entities and persistence models."""

import json
import random
from datetime import datetime

import pygame

from snake_app.constants import FOOD_COLOR, GRID_SIZE, HEIGHT, LEADERBOARD_FILE, WIDTH


class Leaderboard:
    """Store top scores on disk."""

    def __init__(self):
        self.scores = []
        self.load()

    def load(self):
        """Load leaderboard entries from disk."""
        try:
            with LEADERBOARD_FILE.open("r", encoding="utf-8") as file:
                self.scores = json.load(file)
        except FileNotFoundError:
            self.scores = []

    def save(self):
        """Save leaderboard entries to disk."""
        with LEADERBOARD_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.scores, file)

    def add_score(self, username, score):
        """Insert or update a user score, then keep top 10."""
        existing = next(
            (entry for entry in self.scores if entry["username"].lower() == username.lower()),
            None,
        )
        if existing:
            if score > existing["score"]:
                existing["score"] = score
                existing["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            self.scores.append(
                {
                    "username": username,
                    "score": score,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )
        self.scores.sort(key=lambda entry: entry["score"], reverse=True)
        self.scores = self.scores[:10]
        self.save()


class Snake:
    """Runtime snake state and movement rules."""

    def __init__(self):
        self.head = [WIDTH // 2, HEIGHT // 2]
        self.body = []
        self.direction = "RIGHT"
        self.new_direction = "RIGHT"
        self.grow = False

    def move(self):
        """Move one grid step while blocking instant reversal."""
        if self.new_direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
        if self.new_direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        if self.new_direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        if self.new_direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"

        self.body.insert(0, self.head.copy())
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

        if self.direction == "RIGHT":
            self.head[0] += GRID_SIZE
        elif self.direction == "LEFT":
            self.head[0] -= GRID_SIZE
        elif self.direction == "UP":
            self.head[1] -= GRID_SIZE
        elif self.direction == "DOWN":
            self.head[1] += GRID_SIZE


class Food:
    """Normal food pickup and its particles."""

    def __init__(self):
        self.position = [0, 0]
        self.particles = []
        self.spawn()

    def spawn(self):
        """Spawn food away from score and pause UI areas."""
        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        while True:
            x = random.randrange(0, WIDTH, GRID_SIZE)
            y = random.randrange(0, HEIGHT, GRID_SIZE)
            food_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if food_rect.colliderect(forbidden_pause) or food_rect.colliderect(forbidden_score):
                continue
            self.position = [x, y]
            return

    def create_particles(self):
        """Create burst particles at current food position."""
        for _ in range(10):
            self.particles.append(
                [
                    self.position[0] + GRID_SIZE // 2,
                    self.position[1] + GRID_SIZE // 2,
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    random.randint(3, 6),
                ]
            )

    def update_particles(self):
        """Advance and expire food particles."""
        for particle in self.particles[:]:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] -= 0.1
            if particle[4] <= 0:
                self.particles.remove(particle)


class SpecialFood:
    """Special two-cell food that moves and scores double."""

    def __init__(self, food_image):
        self.food_image1 = food_image.copy()
        self.food_image2 = food_image.copy()
        self.food_image1.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
        self.food_image2.fill((255, 255, 0), special_flags=pygame.BLEND_MULT)
        self.dx = random.choice([-5, -4, 4, 5])
        self.dy = random.choice([-5, -4, 4, 5])
        self.points = 20
        self.particles = []
        self.spawn()

    def spawn(self):
        """Spawn special food away from score and pause UI areas."""
        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        while True:
            x = random.randrange(0, WIDTH - 2 * GRID_SIZE, GRID_SIZE)
            y = random.randrange(0, HEIGHT - GRID_SIZE, GRID_SIZE)
            special_rect = pygame.Rect(x, y, 2 * GRID_SIZE, GRID_SIZE)
            if special_rect.colliderect(forbidden_pause) or special_rect.colliderect(forbidden_score):
                continue
            self.x = x
            self.y = y
            return

    def update(self):
        """Move special food and bounce off blocked areas."""
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH - 2 * GRID_SIZE:
            self.dx = -self.dx
            self.x += self.dx
        if self.y < 0 or self.y > HEIGHT - GRID_SIZE:
            self.dy = -self.dy
            self.y += self.dy

        forbidden_pause = pygame.Rect(WIDTH - 60, 20, 40, 40)
        forbidden_score = pygame.Rect(0, 0, 150, 50)
        if self.get_rect().colliderect(forbidden_pause) or self.get_rect().colliderect(forbidden_score):
            self.dx = -self.dx
            self.dy = -self.dy
            self.x += self.dx
            self.y += self.dy

    def draw(self, surface):
        """Draw both special food cells."""
        surface.blit(self.food_image1, (self.x, self.y))
        surface.blit(self.food_image2, (self.x + GRID_SIZE, self.y))

    def get_rect(self):
        """Return special food collision bounds."""
        return pygame.Rect(self.x, self.y, 2 * GRID_SIZE, GRID_SIZE)

    def create_particles(self):
        """Create burst particles at current special food position."""
        for _ in range(10):
            self.particles.append(
                [
                    self.x + GRID_SIZE,
                    self.y + GRID_SIZE // 2,
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    random.randint(3, 6),
                ]
            )

    def update_particles(self):
        """Advance and expire special food particles."""
        for particle in self.particles[:]:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] -= 0.1
            if particle[4] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        """Draw special food particles to screen."""
        for particle in self.particles:
            pygame.draw.circle(surface, FOOD_COLOR, (int(particle[0]), int(particle[1])), int(particle[4]))
