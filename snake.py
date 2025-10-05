import pygame
import sys
import random
from collections import deque
from pathlib import Path

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 24
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 12

ASSETS_DIR = Path("assets")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)

def grid_to_pixel(pos):
    x, y = pos
    return x * CELL_SIZE, y * CELL_SIZE

def random_empty_cell(occupied):
    while True:
        x = random.randrange(GRID_WIDTH)
        y = random.randrange(GRID_HEIGHT)
        if (x, y) not in occupied:
            return (x, y)

def load_image_scaled(path, size):
    try:
        surf = pygame.image.load(str(path)).convert_alpha()
        return pygame.transform.smoothscale(surf, size)
    except Exception:
        return None

class Snake:
    def __init__(self):
        midx, midy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.segments = deque([(midx, midy), (midx - 1, midy), (midx - 2, midy)])
        self.direction = (1, 0)
        self.grow_pending = 0
        self.alive = True

    def head(self): return self.segments[0]

    def move(self):
        if not self.alive: return
        dx, dy = self.direction
        hx, hy = self.head()
        new_head = ((hx + dx) % GRID_WIDTH, (hy + dy) % GRID_HEIGHT)
        if new_head in self.segments:  # collision with itself
            self.alive = False
            return
        self.segments.appendleft(new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()

    def set_direction(self, new_dir):
        dx, dy = new_dir
        cdx, cdy = self.direction
        if (dx == -cdx and dy == -cdy) and len(self.segments) > 1:
            return
        self.direction = (dx, dy)

    def grow(self, n=1): self.grow_pending += n

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game - Commit 2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        # Load assets
        self.bg_img = load_image_scaled(ASSETS_DIR / "bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.apple_img = load_image_scaled(ASSETS_DIR / "apple.png", (CELL_SIZE, CELL_SIZE))

        self.reset()

    def reset(self):
        self.snake = Snake()
        self.score = 0
        self.apple = random_empty_cell(set(self.snake.segments))

    def update(self):
        self.snake.move()
        if not self.snake.alive:
            return
        if self.snake.head() == self.apple:
            self.snake.grow(1)
            self.score += 10
            self.apple = random_empty_cell(set(self.snake.segments))

    def draw(self):
        # background
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BLACK)

        # draw snake
        for i, seg in enumerate(self.snake.segments):
            x, y = grid_to_pixel(seg)
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))

        # draw apple
        ax, ay = grid_to_pixel(self.apple)
        if self.apple_img:
            self.screen.blit(self.apple_img, (ax, ay))
        else:
            pygame.draw.circle(self.screen, (255, 0, 0), (ax + CELL_SIZE//2, ay + CELL_SIZE//2), CELL_SIZE//2)

        # draw score
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))

        if not self.snake.alive:
            gameover = self.font.render("Game Over! Press R to restart", True, WHITE)
            self.screen.blit(gameover, (SCREEN_WIDTH//2 - gameover.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: self.snake.set_direction((0, -1))
            elif event.key == pygame.K_DOWN: self.snake.set_direction((0, 1))
            elif event.key == pygame.K_LEFT: self.snake.set_direction((-1, 0))
            elif event.key == pygame.K_RIGHT: self.snake.set_direction((1, 0))
            elif event.key == pygame.K_r and not self.snake.alive: self.reset()
            elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_input(event)

            if self.snake.alive:
                self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
