import pygame
import random
import sys
from collections import deque
from pathlib import Path
import time



CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 24
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT + 80
FPS = 12

ASSETS_DIR = Path("assets")
SOUNDS_DIR = ASSETS_DIR / "sounds"

WHITE = (255, 255, 255)
BLACK = (8, 8, 10)
GRAY = (100, 100, 110)
GOLD = (215, 170, 60)
RED = (180, 30, 30)
GREEN = (50, 200, 100)
DARK_GREEN = (20, 90, 50)
FAITH_BG = (40, 40, 60)
PURPLE = (160, 80, 200)

GAME_TITLE = "SACRIFICES MUST BE MADE"


def grid_to_pixel(pos):
    x, y = pos
    return x * CELL_SIZE, y * CELL_SIZE


def random_empty_cell(occupied):
    while True:
        x = random.randrange(0, GRID_WIDTH)
        y = random.randrange(0, GRID_HEIGHT)
        if (x, y) not in occupied:
            return (x, y)


def load_image_scaled(path, size):
    try:
        surf = pygame.image.load(str(path)).convert_alpha()
        return pygame.transform.smoothscale(surf, size)
    except Exception:
        return None


def load_sound(path):
    try:
        return pygame.mixer.Sound(str(path))
    except Exception:
        return None



class Snake:
    def __init__(self):
        midx, midy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.segments = deque([(midx, midy), (midx - 1, midy), (midx - 2, midy)])
        self.direction = (1, 0)
        self.grow_pending = 0
        self.alive = True


    def head(self): 
        return self.segments[0]


    def move(self):
        if not self.alive: 
            return
        dx, dy = self.direction
        hx, hy = self.head()
        new_head = ((hx + dx) % GRID_WIDTH, (hy + dy) % GRID_HEIGHT)
        self.segments.appendleft(new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()


    def set_direction(self, new_dir, inverted=False):
        dx, dy = new_dir
        if inverted:
            dx, dy = -dx, -dy
        cdx, cdy = self.direction
        if (dx == -cdx and dy == -cdy) and len(self.segments) > 1:
            return
        self.direction = (dx, dy)


    def grow(self, n=1): 
        self.grow_pending += n


    def shorten(self, n):
        for _ in range(n):
            if len(self.segments) > 1:
                self.segments.pop()


    def shrink_half(self):
        half = len(self.segments) // 2
        for _ in range(half):
            if len(self.segments) > 1:
                self.segments.pop()


    def check_self_collision(self):
        head = self.head()
        return head in list(self.segments)[1:]



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.big_font = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.font = pygame.font.SysFont("dejavusans", 18)

        # Assets
        self.bg_img = load_image_scaled(ASSETS_DIR / "bg.png", (SCREEN_WIDTH, GRID_HEIGHT * CELL_SIZE))
        self.apple_img = load_image_scaled(ASSETS_DIR / "apple.png", (CELL_SIZE, CELL_SIZE))
        self.altar_img = load_image_scaled(ASSETS_DIR / "altar.png", (CELL_SIZE, CELL_SIZE))
        self.intro_img = load_image_scaled(ASSETS_DIR / "intro.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Sounds
        self.sfx_eat = load_sound(SOUNDS_DIR / "eat.wav")
        self.sfx_gameover = load_sound(SOUNDS_DIR / "gameover.wav")
        self.music_intro = SOUNDS_DIR / "intro.wav"
        self.music_bg = SOUNDS_DIR / "bg.wav"

        self.in_intro = True
        self.menu_index = 0
        self.reset()


    def reset(self):
        self.snake = Snake()
        self.score = 0
        self.multiplier = 1.5
        self.paused = False
        self.altar_pos = None
        self.altar_active = False
        self.altar_popup = False
        self.selected_option = 0
        self.last_altar_trigger = 0
        self.offering_pos = random_empty_cell(set(self.snake.segments))
        self.messages = []
        self.inverted_controls = False
        self.invert_end_time = 0
        self.invert_end_score = 0

        pygame.mixer.music.stop()
        pygame.mixer.music.load(str(self.music_bg))
        pygame.mixer.music.play(-1)


    def spawn_altar(self):
        occupied = set(self.snake.segments)
        while True:
            x = random.randrange(0, GRID_WIDTH - 3)
            y = random.randrange(0, GRID_HEIGHT - 3)
            cells = [(x+i, y+j) for i in range(4) for j in range(4)]
            if not any(c in occupied for c in cells):
                self.altar_pos = (x, y)
                self.altar_active = True
                break


    def altar_cells(self):
        if not self.altar_pos: 
            return []
        ax, ay = self.altar_pos
        return [(ax+i, ay+j) for i in range(4) for j in range(4)]


    def update(self):
        if self.paused or self.altar_popup or not self.snake.alive or self.in_intro:
            return

        self.snake.move()

        if self.snake.check_self_collision():
            self.snake.alive = False
            if self.sfx_gameover: self.sfx_gameover.play()
            return

        # Eat apple
        if self.snake.head() == self.offering_pos:
            self.score += 10 * self.multiplier
            self.snake.grow(1)
            self.offering_pos = random_empty_cell(set(self.snake.segments))
            if self.sfx_eat: self.sfx_eat.play()

        # Spawn altar
        if self.score - self.last_altar_trigger >= 225 and not self.altar_active:
            self.spawn_altar()
            self.last_altar_trigger = self.score

        # Auto altar activation on collision
        if self.altar_active and self.snake.head() in self.altar_cells():
            self.altar_popup = True
            self.selected_option = 0

        # Handle inverted controls expiry
        if self.inverted_controls:
            if time.time() > self.invert_end_time or self.score >= self.invert_end_score:
                self.inverted_controls = False
                self.messages.append(["Inversion faded.", FPS * 3])


    def apply_choice(self):
        self.altar_popup = False
        self.altar_active = False
        msg = ""

        if self.selected_option == 0:
            pts = random.randint(1, 50)
            msg = f"Embrace Greed: +{pts} pts"
            self.score += pts
            self.snake.grow(max(1, pts // 10))

        elif self.selected_option == 1:
            if len(self.snake.segments) > 4:
                self.snake.shorten(3)
            self.multiplier = max(0.5, round(self.multiplier - 0.1, 2))
            msg = f"Sacrifice Self: Multiplier {self.multiplier:.1f}x"

        elif self.selected_option == 2:
            self.snake.shrink_half()
            self.multiplier = 0.5
            msg = "Halve Thyself: Multiplier fixed at 0.5x"

        elif self.selected_option == 3:
            self.inverted_controls = True
            self.multiplier += 1.0
            self.invert_end_time = time.time() + 20
            self.invert_end_score = self.score + 100
            msg = f"Twisted Fate: +1x, controls inverted!"

        self.messages.append([msg, FPS * 3])


    def draw_background(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BLACK)


    def draw_snake(self):
        for i, seg in enumerate(self.snake.segments):
            x, y = grid_to_pixel(seg)
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)


    def draw_altar(self):
        if not self.altar_active: 
            return
        ax, ay = self.altar_pos
        px, py = grid_to_pixel((ax, ay))
        altar_size = (CELL_SIZE * 4, CELL_SIZE * 4)

        if self.altar_img:
            big_altar = pygame.transform.smoothscale(self.altar_img, altar_size)
            self.screen.blit(big_altar, (px, py))
        else:
            pygame.draw.rect(self.screen, PURPLE, (px, py, altar_size[0], altar_size[1]))


    def draw_apple(self):
        x, y = grid_to_pixel(self.offering_pos)
        if self.apple_img:
            self.screen.blit(self.apple_img, (x, y))
        else:
            pygame.draw.circle(self.screen, GOLD, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//2 - 2)


    def draw_hud(self):
        hud_rect = pygame.Rect(0, GRID_HEIGHT * CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, FAITH_BG, hud_rect)

        title = self.big_font.render(GAME_TITLE, True, WHITE)
        self.screen.blit(title, (10, GRID_HEIGHT * CELL_SIZE + 4))

        score_text = self.font.render(f"Score: {int(self.score)}   x{self.multiplier:.1f}", True, GOLD)
        self.screen.blit(score_text, (10, GRID_HEIGHT * CELL_SIZE + 40))

        if not self.snake.alive:
            over = self.big_font.render("You Fell.", True, RED)
            sub = self.font.render("Press R to restart.", True, WHITE)
            self.screen.blit(over, (SCREEN_WIDTH//2 - over.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2))

        if self.inverted_controls:
            warn = self.font.render("⚡ Inverted Controls Active!", True, RED)
            self.screen.blit(warn, (SCREEN_WIDTH - warn.get_width() - 10, GRID_HEIGHT * CELL_SIZE + 40))

        for i, (txt, t) in enumerate(list(self.messages)):
            m = self.font.render(txt, True, WHITE)
            self.screen.blit(m, (10, GRID_HEIGHT * CELL_SIZE - i*22))
            self.messages[i][1] -= 1
            if self.messages[i][1] <= 0:
                self.messages.remove(self.messages[i])


    def draw_popup(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        options = [
            "1. Embrace Greed  (+ 1–50 pts, grow slightly)",
            "2. Sacrifice Self  (-3 length, -0.1x multiplier)",
            "3. Halve Thyself  (shrink half, multiplier=0.5x)",
            "4. Twisted Fate  (invert controls, +1x for 20s/100pts)"
        ]

        bx = SCREEN_WIDTH // 2 - 260
        by = SCREEN_HEIGHT // 2 - 120
        pygame.draw.rect(self.screen, (50, 40, 60), (bx, by, 520, 220))
        pygame.draw.rect(self.screen, WHITE, (bx, by, 520, 220), 2)

        title = self.big_font.render("The Altar Awaits...", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, by + 10))

        for i, opt in enumerate(options):
            color = GOLD if i == self.selected_option else WHITE
            txt = self.font.render(opt, True, color)
            self.screen.blit(txt, (bx + 40, by + 60 + i*35))

        hint = self.font.render("Use ↑↓ and Enter to choose", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, by + 175))


    def draw_intro(self):
        if self.intro_img:
            self.screen.blit(self.intro_img, (0, 0))
        else:
            self.screen.fill(BLACK)

        options = ["New Game", "Exit"]
        for i, opt in enumerate(options):
            color = GOLD if i == self.menu_index else WHITE
            txt = self.big_font.render(opt, True, color)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 250 + i*60))


    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.in_intro:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_index = (self.menu_index - 1) % 2
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_index = (self.menu_index + 1) % 2
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.menu_index == 0:
                        self.in_intro = False
                        self.reset()
                    else:
                        pygame.quit(); sys.exit()
            elif self.altar_popup:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_option = (self.selected_option - 1) % 4
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_option = (self.selected_option + 1) % 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.apply_choice()
            else:
                if event.key == pygame.K_UP: self.snake.set_direction((0, -1), self.inverted_controls)
                elif event.key == pygame.K_DOWN: self.snake.set_direction((0, 1), self.inverted_controls)
                elif event.key == pygame.K_LEFT: self.snake.set_direction((-1, 0), self.inverted_controls)
                elif event.key == pygame.K_RIGHT: self.snake.set_direction((1, 0), self.inverted_controls)
                elif event.key == pygame.K_p: self.paused = not self.paused
                elif event.key == pygame.K_r and not self.snake.alive: self.reset()
                elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()


    def run(self):
        pygame.mixer.music.load(str(self.music_intro))
        pygame.mixer.music.play(-1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_input(event)

            if self.in_intro:
                self.draw_intro()
            else:
                self.update()
                self.draw_background()
                self.draw_apple()
                self.draw_altar()
                self.draw_snake()
                self.draw_hud()
                if self.altar_popup: self.draw_popup()

            pygame.display.flip()
            self.clock.tick(FPS)



if __name__ == "__main__":
    Game().run()
