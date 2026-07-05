import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# ============================================
# GAME CONSTANTS
# ============================================
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
SKY_BLUE = (107, 140, 255)
SKY_DARK = (50, 80, 180)
SKY_NIGHT = (20, 20, 50)
SKY_CASTLE = (40, 0, 0)
GROUND_COLOR = (139, 69, 19)
PIPE_GREEN = (0, 168, 0)
PIPE_DARK = (0, 100, 0)
BRICK_COLOR = (165, 42, 42)
COIN_YELLOW = (255, 215, 0)
GOOMBA_BROWN = (139, 69, 19)
MARIO_RED = (255, 0, 0)
MARIO_BLUE = (0, 0, 255)
MARIO_SKIN = (255, 200, 150)
MARIO_BROWN = (101, 67, 33)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (101, 67, 33)
PINK = (255, 192, 203)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = 16
PLAYER_SPEED = 5

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros - Python Edition - 12 Stages")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 24)
medium_font = pygame.font.SysFont('Arial', 32)
large_font = pygame.font.SysFont('Arial', 48)
huge_font = pygame.font.SysFont('Arial', 72)


# ============================================
# HELPER FUNCTIONS
# ============================================
def draw_text(text, font_obj, color, x, y, center=True):
    """Helper function to draw text on screen"""
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def draw_clouds(offset=0):
    """Draw decorative clouds in the background"""
    cloud_positions = [(100, 60), (350, 40), (600, 80), (150, 120), (500, 100),
                       (250, 90), (700, 50), (450, 130)]
    for cx, cy in cloud_positions:
        x = (cx - offset) % (WIDTH + 200) - 100
        pygame.draw.circle(screen, WHITE, (x, cy), 20)
        pygame.draw.circle(screen, WHITE, (x + 20, cy), 25)
        pygame.draw.circle(screen, WHITE, (x + 40, cy), 20)
        pygame.draw.rect(screen, WHITE, (x + 10, cy - 5, 25, 20))


def draw_hills(offset=0, hill_color=GREEN):
    """Draw rolling hills in the background"""
    hill_positions = [(50, HEIGHT - 80), (300, HEIGHT - 80), (550, HEIGHT - 80),
                      (750, HEIGHT - 80), (200, HEIGHT - 80)]
    for hx, hy in hill_positions:
        x = (hx - offset) % (WIDTH + 300) - 150
        pygame.draw.ellipse(screen, hill_color, (x, hy, 250, 100))


def draw_stars():
    """Draw twinkling stars for night levels"""
    import time
    for i in range(50):
        x = (i * 137) % WIDTH
        y = (i * 53) % (HEIGHT // 2)
        size = 1 + (i % 3)
        brightness = 200 + int(55 * math.sin(time.time() * 2 + i))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (x, y), size)


# ============================================
# SPRITE CLASSES
# ============================================
class Player(pygame.sprite.Sprite):
    """The Mario character"""
    
    def __init__(self, x, y):
        super().__init__()
        self.original_image = self.create_mario_sprite()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.start_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.invincible = 0
        self.alive_status = True
        self.power_up = False
        self.walk_frame = 0
    
    def create_mario_sprite(self):
        """Create a Mario-like sprite using simple shapes"""
        surface = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, MARIO_RED, (5, 0, 20, 8))
        pygame.draw.rect(surface, MARIO_RED, (0, 8, 25, 5))
        pygame.draw.rect(surface, WHITE, (10, 4, 10, 4))
        pygame.draw.rect(surface, MARIO_SKIN, (5, 13, 20, 10))
        pygame.draw.rect(surface, BLACK, (10, 16, 3, 3))
        pygame.draw.rect(surface, BLACK, (18, 16, 3, 3))
        pygame.draw.rect(surface, MARIO_BROWN, (8, 21, 14, 2))
        pygame.draw.rect(surface, MARIO_RED, (5, 23, 20, 8))
        pygame.draw.rect(surface, MARIO_BLUE, (3, 31, 24, 9))
        pygame.draw.circle(surface, YELLOW, (10, 35), 2)
        pygame.draw.circle(surface, YELLOW, (20, 35), 2)
        pygame.draw.rect(surface, MARIO_BROWN, (3, 38, 10, 2))
        pygame.draw.rect(surface, MARIO_BROWN, (17, 38, 10, 2))
        return surface
    
    def update(self, platforms):
        """Update player position and handle collisions"""
        if not self.alive_status:
            return
            
        keys = pygame.key.get_pressed()
        
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        
        if self.vel_x != 0 and self.on_ground:
            self.walk_frame += 1
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.on_ground = False
        
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15
        
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
        
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        
        if self.rect.top > HEIGHT:
            self.take_damage()
        
        if self.invincible > 0:
            self.invincible -= 1
            if self.invincible % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    
    def take_damage(self):
        """Player takes damage"""
        self.lives -= 1
        if self.lives > 0:
            self.respawn()
        else:
            self.alive_status = False
    
    def respawn(self):
        """Respawn the player at starting position"""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0
        self.invincible = 90
    
    def stomp_bounce(self):
        """Make player bounce after stomping enemy"""
        self.vel_y = -10
    
    def add_life(self):
        """Add an extra life"""
        self.lives += 1


class Platform(pygame.sprite.Sprite):
    """Static platforms and ground"""
    
    def __init__(self, x, y, width, height, color=GROUND_COLOR, is_pipe=False, is_ground=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        if is_pipe:
            pygame.draw.rect(self.image, PIPE_DARK, (0, 0, width, 12))
            pygame.draw.rect(self.image, (50, 200, 50), (5, 0, width - 10, 6))
            pygame.draw.rect(self.image, (100, 255, 100), (3, 12, 3, height - 12))
        elif is_ground:
            pygame.draw.rect(self.image, GREEN, (0, 0, width, 8))
            for i in range(0, width, 20):
                pygame.draw.line(self.image, DARK_GREEN, (i, 0), (i + 5, 8), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_pipe = is_pipe
        self.is_ground = is_ground


class Brick(pygame.sprite.Sprite):
    """Destructible brick blocks"""
    
    def __init__(self, x, y, has_coin=False):
        super().__init__()
        self.has_coin = has_coin
        self.image = pygame.Surface((40, 40))
        self.image.fill(BRICK_COLOR)
        pygame.draw.rect(self.image, BLACK, (0, 0, 40, 40), 2)
        pygame.draw.line(self.image, BLACK, (0, 20), (40, 20), 2)
        pygame.draw.line(self.image, BLACK, (20, 0), (20, 20), 2)
        pygame.draw.line(self.image, BLACK, (10, 20), (10, 40), 2)
        pygame.draw.line(self.image, BLACK, (30, 20), (30, 40), 2)
        if has_coin:
            pygame.draw.circle(self.image, COIN_YELLOW, (20, 20), 6)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit = False


class QuestionBlock(pygame.sprite.Sprite):
    """Question blocks that give coins"""
    
    def __init__(self, x, y, content="coin"):
        super().__init__()
        self.content = content
        self.image = self.create_question_block()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit = False
        self.bounce_offset = 0
        self.bouncing = False
        self.bounce_vel = 0
    
    def create_question_block(self):
        """Create a question block sprite"""
        surface = pygame.Surface((40, 40))
        surface.fill(ORANGE)
        pygame.draw.rect(surface, BLACK, (0, 0, 40, 40), 3)
        pygame.draw.rect(surface, YELLOW, (5, 5, 30, 30), 2)
        text = font.render("?", True, WHITE)
        surface.blit(text, (15, 10))
        return surface
    
    def update(self):
        """Handle bounce animation"""
        if self.bouncing:
            self.bounce_vel += 1
            self.bounce_offset += self.bounce_vel
            if self.bounce_offset >= 0:
                self.bounce_offset = 0
                self.bouncing = False
                self.bounce_vel = 0
    
    def hit_block(self):
        """Get hit by player"""
        if not self.hit:
            self.hit = True
            self.bouncing = True
            self.bounce_vel = -5
            self.image.fill(BROWN)
            pygame.draw.rect(self.image, BLACK, (0, 0, 40, 40), 2)
            return self.content
        return None


class Enemy(pygame.sprite.Sprite):
    """Goomba enemies that patrol platforms"""
    
    def __init__(self, x, y, patrol_distance=200, enemy_type="goomba"):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = self.create_enemy_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.vel_x = random.choice([-1.5, 1.5])
        self.vel_y = 0
        self.on_ground = False
        self.walk_frame = 0
    
    def create_enemy_sprite(self):
        """Create enemy sprite based on type"""
        if self.enemy_type == "goomba":
            return self.create_goomba()
        elif self.enemy_type == "koopa":
            return self.create_koopa()
        return self.create_goomba()
    
    def create_goomba(self):
        """Create a Goomba-like sprite"""
        surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (0, 8, 30, 22))
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (5, 0, 20, 20))
        pygame.draw.circle(surface, WHITE, (10, 8), 3)
        pygame.draw.circle(surface, WHITE, (20, 8), 3)
        pygame.draw.circle(surface, BLACK, (10, 8), 1)
        pygame.draw.circle(surface, BLACK, (20, 8), 1)
        pygame.draw.rect(surface, BLACK, (7, 4, 6, 2))
        pygame.draw.rect(surface, BLACK, (17, 4, 6, 2))
        pygame.draw.ellipse(surface, (100, 50, 0), (0, 25, 12, 8))
        pygame.draw.ellipse(surface, (100, 50, 0), (18, 25, 12, 8))
        return surface
    
    def create_koopa(self):
        """Create a Koopa Troopa sprite"""
        surface = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, GREEN, (5, 15, 20, 25))
        pygame.draw.ellipse(surface, YELLOW, (8, 18, 14, 19))
        pygame.draw.circle(surface, GREEN, (15, 10), 10)
        pygame.draw.circle(surface, WHITE, (12, 8), 3)
        pygame.draw.circle(surface, WHITE, (18, 8), 3)
        pygame.draw.circle(surface, BLACK, (12, 9), 1)
        pygame.draw.circle(surface, BLACK, (18, 9), 1)
        pygame.draw.ellipse(surface, ORANGE, (5, 35, 8, 5))
        pygame.draw.ellipse(surface, ORANGE, (17, 35, 8, 5))
        return surface
    
    def update(self, platforms):
        """Update enemy position and patrol behavior"""
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15
        
        self.rect.x += self.vel_x
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = -abs(self.vel_x)
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = abs(self.vel_x)
        
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.vel_x *= -1


class Coin(pygame.sprite.Sprite):
    """Collectible coins"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = self.create_coin_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False
        self.frame = 0
    
    def create_coin_sprite(self):
        """Create a coin sprite"""
        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surface, COIN_YELLOW, (10, 10), 8)
        pygame.draw.circle(surface, (200, 150, 0), (10, 10), 8, 2)
        pygame.draw.rect(surface, (200, 150, 0), (8, 3, 4, 14))
        return surface
    
    def update(self):
        """Animate the coin"""
        self.frame += 1


class PowerUp(pygame.sprite.Sprite):
    """Mushroom power-up"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = self.create_mushroom()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 2
        self.vel_y = 0
    
    def create_mushroom(self):
        """Create a super mushroom sprite"""
        # FIXED: Added missing opening parenthesis
        surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, RED, (0, 0, 30, 18))
        pygame.draw.circle(surface, WHITE, (8, 8), 3)
        pygame.draw.circle(surface, WHITE, (22, 8), 3)
        pygame.draw.circle(surface, WHITE, (15, 5), 2)
        pygame.draw.ellipse(surface, (255, 220, 177), (5, 15, 20, 15))
        pygame.draw.circle(surface, BLACK, (12, 22), 2)
        pygame.draw.circle(surface, BLACK, (18, 22), 2)
        return surface
    
    def update(self, platforms):
        """Move power-up and handle physics"""
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = -self.vel_x
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = -self.vel_x
        
        self.rect.y += self.vel_y
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0


class Flag(pygame.sprite.Sprite):
    """The goal/flag to reach"""
    
    def __init__(self, x, y, height=200):
        super().__init__()
        self.image = self.create_flag_sprite(height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def create_flag_sprite(self, height):
        """Create the flag pole and flag"""
        surface = pygame.Surface((40, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (200, 200, 200), (18, 0, 4, height))
        pygame.draw.polygon(surface, GREEN, [(22, 20), (40, 30), (22, 40)])
        pygame.draw.circle(surface, (255, 215, 0), (20, 5), 5)
        return surface


# ============================================
# LEVEL DEFINITIONS
# ============================================
class Level:
    """Class to define each level/stage"""
    
    def __init__(self, number, name, sky_color, ground_color, 
                 platforms_list, bricks_list, question_blocks_list,
                 enemies_list, coins_list, flag_pos, 
                 time_limit=300, theme="normal"):
        self.number = number
        self.name = name
        self.sky_color = sky_color
        self.ground_color = ground_color
        self.platforms_list = platforms_list
        self.bricks_list = bricks_list
        self.question_blocks_list = question_blocks_list
        self.enemies_list = enemies_list
        self.coins_list = coins_list
        self.flag_pos = flag_pos
        self.time_limit = time_limit
        self.theme = theme


# Define all 12 levels with increasing difficulty
LEVELS = [
    Level(
        number=1, name="World 1-1: Welcome to Mario!",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (200, 450, 150, 20, GROUND_COLOR, False),
            (450, 350, 150, 20, GROUND_COLOR, False),
            (100, 280, 100, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(250, 200, False)],
        question_blocks_list=[(300, 200, "coin"), (350, 200, "coin")],
        enemies_list=[(400, HEIGHT - 70, 150, "goomba")],
        coins_list=[(250, 420), (500, 320), (130, 250), (700, HEIGHT - 70), (270, 170), (320, 170)],
        flag_pos=(750, HEIGHT - 240), time_limit=300
    ),
    Level(
        number=2, name="World 1-2: Pipe Madness",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (150, 480, 80, 20, GROUND_COLOR, False),
            (350, 420, 100, 20, GROUND_COLOR, False),
            (550, 360, 120, 20, GROUND_COLOR, False),
            (200, 280, 100, 20, GROUND_COLOR, False),
            (500, 200, 100, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(350, 420, False), (390, 420, True), (430, 420, False)],
        question_blocks_list=[(250, 280, "coin")],
        enemies_list=[(300, HEIGHT - 70, 100, "goomba"), (600, HEIGHT - 70, 120, "goomba")],
        coins_list=[(180, 450), (380, 390), (580, 330), (230, 250), (400, HEIGHT - 70), (700, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=280
    ),
    Level(
        number=3, name="World 2-1: Underground",
        sky_color=SKY_DARK, ground_color=DARK_GRAY,
        platforms_list=[
            (100, 500, 100, 20, DARK_GRAY, False),
            (300, 450, 120, 20, DARK_GRAY, False),
            (500, 400, 100, 20, DARK_GRAY, False),
            (200, 350, 100, 20, DARK_GRAY, False),
            (400, 300, 100, 20, DARK_GRAY, False),
            (600, 250, 100, 20, DARK_GRAY, False),
        ],
        bricks_list=[(200, 350, False), (240, 350, False)],
        question_blocks_list=[(400, 300, "coin"), (440, 300, "power")],
        enemies_list=[(250, HEIGHT - 70, 80, "goomba"), (450, HEIGHT - 70, 100, "goomba"), (150, 480, 50, "goomba")],
        coins_list=[(150, 470), (350, 420), (550, 370), (250, 320), (450, 270), (650, 220), (350, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=260
    ),
    Level(
        number=4, name="World 2-2: Goomba Army",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (150, 450, 100, 20, GROUND_COLOR, False),
            (350, 380, 120, 20, GROUND_COLOR, False),
            (550, 310, 100, 20, GROUND_COLOR, False),
            (200, 250, 80, 20, GROUND_COLOR, False),
            (450, 200, 100, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(250, 450, False), (290, 450, True)],
        question_blocks_list=[(450, 200, "coin"), (490, 200, "coin")],
        enemies_list=[(200, HEIGHT - 70, 80, "goomba"), (400, HEIGHT - 70, 100, "goomba"), (600, HEIGHT - 70, 80, "goomba"), (350, 360, 60, "goomba"), (500, 290, 60, "koopa")],
        coins_list=[(180, 420), (380, 350), (580, 280), (230, 220), (480, 170), (300, HEIGHT - 70), (500, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=240
    ),
    Level(
        number=5, name="World 3-1: Sky High",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (100, 450, 80, 20, GROUND_COLOR, False),
            (250, 400, 80, 20, GROUND_COLOR, False),
            (400, 350, 80, 20, GROUND_COLOR, False),
            (550, 300, 80, 20, GROUND_COLOR, False),
            (700, 250, 80, 20, GROUND_COLOR, False),
            (150, 200, 80, 20, GROUND_COLOR, False),
            (350, 150, 80, 20, GROUND_COLOR, False),
            (550, 100, 80, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(250, 400, False)],
        question_blocks_list=[(400, 350, "coin"), (550, 300, "coin")],
        enemies_list=[(300, HEIGHT - 70, 80, "goomba"), (500, HEIGHT - 70, 100, "goomba"), (700, HEIGHT - 70, 60, "goomba"), (550, 80, 40, "koopa")],
        coins_list=[(130, 420), (280, 370), (430, 320), (580, 270), (730, 220), (180, 170), (380, 120), (580, 70), (400, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=220
    ),
    Level(
        number=6, name="World 4-1: Castle Approach",
        sky_color=SKY_NIGHT, ground_color=DARK_GRAY,
        platforms_list=[
            (100, 480, 80, 20, DARK_GRAY, False),
            (250, 420, 100, 20, DARK_GRAY, False),
            (400, 360, 80, 20, DARK_GRAY, False),
            (550, 300, 100, 20, DARK_GRAY, False),
            (200, 240, 80, 20, DARK_GRAY, False),
            (450, 180, 100, 20, DARK_GRAY, False),
        ],
        bricks_list=[(250, 420, True), (290, 420, False)],
        question_blocks_list=[(400, 360, "coin"), (550, 300, "power")],
        enemies_list=[(200, HEIGHT - 70, 80, "goomba"), (400, HEIGHT - 70, 100, "goomba"), (600, HEIGHT - 70, 80, "goomba"), (300, 400, 50, "goomba"), (500, 340, 50, "koopa")],
        coins_list=[(150, 450), (300, 390), (430, 330), (600, 270), (230, 210), (500, 150), (350, HEIGHT - 70), (550, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=200
    ),
    Level(
        number=7, name="World 4-2: Lava Castle",
        sky_color=SKY_CASTLE, ground_color=DARK_GRAY,
        platforms_list=[
            (100, 500, 60, 20, DARK_GRAY, False),
            (220, 450, 60, 20, DARK_GRAY, False),
            (340, 400, 60, 20, DARK_GRAY, False),
            (460, 350, 60, 20, DARK_GRAY, False),
            (580, 300, 60, 20, DARK_GRAY, False),
            (200, 200, 80, 20, DARK_GRAY, False),
            (400, 150, 80, 20, DARK_GRAY, False),
        ],
        bricks_list=[(220, 450, False)],
        question_blocks_list=[(340, 400, "coin"), (460, 350, "coin")],
        enemies_list=[(150, HEIGHT - 70, 60, "goomba"), (300, HEIGHT - 70, 60, "goomba"), (450, HEIGHT - 70, 60, "goomba"), (600, HEIGHT - 70, 60, "goomba"), (250, 430, 30, "goomba"), (480, 330, 30, "koopa")],
        coins_list=[(130, 470), (250, 420), (370, 370), (490, 320), (610, 270), (230, 170), (430, 120), (200, HEIGHT - 70), (500, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=200
    ),
    Level(
        number=8, name="World 5-1: Tower Climb",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (100, 520, 80, 20, GROUND_COLOR, False),
            (250, 480, 60, 20, GROUND_COLOR, False),
            (150, 420, 60, 20, GROUND_COLOR, False),
            (300, 360, 60, 20, GROUND_COLOR, False),
            (200, 300, 60, 20, GROUND_COLOR, False),
            (350, 240, 60, 20, GROUND_COLOR, False),
            (500, 200, 80, 20, GROUND_COLOR, False),
            (200, 160, 60, 20, GROUND_COLOR, False),
            (400, 120, 80, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(300, 360, True)],
        question_blocks_list=[(200, 300, "coin"), (350, 240, "coin"), (500, 200, "power")],
        enemies_list=[(300, HEIGHT - 70, 60, "goomba"), (500, HEIGHT - 70, 80, "goomba"), (700, HEIGHT - 70, 50, "goomba"), (200, 300, 30, "goomba"), (450, 180, 30, "koopa")],
        coins_list=[(130, 490), (270, 450), (170, 390), (320, 330), (220, 270), (370, 210), (530, 170), (220, 130), (430, 90), (400, HEIGHT - 70), (600, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=180
    ),
    Level(
        number=9, name="World 6-1: Speed Run",
        sky_color=SKY_BLUE, ground_color=GROUND_COLOR,
        platforms_list=[
            (100, 500, 50, 20, GROUND_COLOR, False),
            (200, 450, 50, 20, GROUND_COLOR, False),
            (300, 400, 50, 20, GROUND_COLOR, False),
            (400, 350, 50, 20, GROUND_COLOR, False),
            (500, 300, 50, 20, GROUND_COLOR, False),
            (600, 250, 50, 20, GROUND_COLOR, False),
            (100, 200, 100, 20, GROUND_COLOR, False),
            (300, 150, 100, 20, GROUND_COLOR, False),
            (500, 100, 100, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(100, 200, False), (140, 200, False)],
        question_blocks_list=[(300, 150, "coin"), (340, 150, "coin"), (500, 100, "coin")],
        enemies_list=[(150, HEIGHT - 70, 40, "goomba"), (250, HEIGHT - 70, 40, "goomba"), (350, HEIGHT - 70, 40, "goomba"), (450, HEIGHT - 70, 40, "goomba"), (550, HEIGHT - 70, 40, "goomba"), (650, HEIGHT - 70, 40, "goomba"), (350, 130, 50, "goomba"), (520, 80, 40, "koopa")],
        coins_list=[(110, 470), (210, 420), (310, 370), (410, 320), (510, 270), (610, 220), (150, 170), (350, 120), (550, 70), (300, HEIGHT - 70), (500, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=150
    ),
    Level(
        number=10, name="World 7-1: Bowser's Castle",
        sky_color=SKY_CASTLE, ground_color=DARK_GRAY,
        platforms_list=[
            (50, 520, 60, 20, DARK_GRAY, False),
            (150, 470, 50, 20, DARK_GRAY, False),
            (250, 420, 50, 20, DARK_GRAY, False),
            (350, 370, 50, 20, DARK_GRAY, False),
            (450, 320, 50, 20, DARK_GRAY, False),
            (550, 270, 50, 20, DARK_GRAY, False),
            (650, 220, 50, 20, DARK_GRAY, False),
            (100, 180, 80, 20, DARK_GRAY, False),
            (300, 130, 80, 20, DARK_GRAY, False),
            (500, 80, 80, 20, DARK_GRAY, False),
        ],
        bricks_list=[(150, 470, False), (350, 370, True)],
        question_blocks_list=[(250, 420, "coin"), (450, 320, "coin"), (550, 270, "power"), (300, 130, "coin"), (500, 80, "coin")],
        enemies_list=[(100, HEIGHT - 70, 30, "goomba"), (200, HEIGHT - 70, 30, "goomba"), (300, HEIGHT - 70, 30, "goomba"), (400, HEIGHT - 70, 30, "goomba"), (500, HEIGHT - 70, 30, "goomba"), (600, HEIGHT - 70, 30, "goomba"), (700, HEIGHT - 70, 30, "goomba"), (300, 350, 25, "goomba"), (500, 250, 25, "koopa"), (600, 200, 25, "koopa"), (350, 110, 40, "goomba")],
        coins_list=[(80, 490), (180, 440), (280, 390), (380, 340), (480, 290), (580, 240), (680, 190), (150, 150), (350, 100), (550, 50), (200, HEIGHT - 70), (500, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=150
    ),
    Level(
        number=11, name="BONUS: Sky Paradise",
        sky_color=(135, 206, 250), ground_color=GROUND_COLOR,
        platforms_list=[
            (100, 500, 80, 20, GROUND_COLOR, False),
            (250, 450, 60, 20, GROUND_COLOR, False),
            (400, 400, 60, 20, GROUND_COLOR, False),
            (550, 350, 60, 20, GROUND_COLOR, False),
            (150, 300, 80, 20, GROUND_COLOR, False),
            (350, 250, 80, 20, GROUND_COLOR, False),
            (550, 200, 80, 20, GROUND_COLOR, False),
            (200, 150, 80, 20, GROUND_COLOR, False),
            (500, 100, 80, 20, GROUND_COLOR, False),
        ],
        bricks_list=[(250, 450, False), (290, 450, True)],
        question_blocks_list=[(400, 400, "coin"), (550, 350, "coin"), (350, 250, "coin"), (550, 200, "coin"), (500, 100, "power")],
        enemies_list=[(300, HEIGHT - 70, 60, "goomba"), (600, HEIGHT - 70, 60, "goomba"), (400, 380, 30, "goomba")],
        coins_list=[(130, 470), (280, 420), (430, 370), (580, 320), (180, 270), (380, 220), (580, 170), (230, 120), (530, 70), (250, HEIGHT - 70), (500, HEIGHT - 70), (700, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=200
    ),
    Level(
        number=12, name="FINAL: Ultimate Challenge",
        sky_color=SKY_CASTLE, ground_color=DARK_GRAY,
        platforms_list=[
            (50, 540, 50, 20, DARK_GRAY, False),
            (130, 490, 50, 20, DARK_GRAY, False),
            (210, 440, 50, 20, DARK_GRAY, False),
            (290, 390, 50, 20, DARK_GRAY, False),
            (370, 340, 50, 20, DARK_GRAY, False),
            (450, 290, 50, 20, DARK_GRAY, False),
            (530, 240, 50, 20, DARK_GRAY, False),
            (610, 190, 50, 20, DARK_GRAY, False),
            (690, 140, 50, 20, DARK_GRAY, False),
            (100, 200, 100, 20, DARK_GRAY, False),
            (300, 150, 100, 20, DARK_GRAY, False),
            (500, 100, 100, 20, DARK_GRAY, False),
        ],
        bricks_list=[(210, 440, True), (530, 240, False)],
        question_blocks_list=[(290, 390, "coin"), (450, 290, "coin"), (610, 190, "coin"), (100, 200, "power"), (300, 150, "coin"), (500, 100, "coin")],
        enemies_list=[(100, HEIGHT - 70, 25, "goomba"), (200, HEIGHT - 70, 25, "goomba"), (300, HEIGHT - 70, 25, "goomba"), (400, HEIGHT - 70, 25, "goomba"), (500, HEIGHT - 70, 25, "goomba"), (600, HEIGHT - 70, 25, "goomba"), (700, HEIGHT - 70, 25, "goomba"), (300, 370, 25, "goomba"), (470, 270, 25, "koopa"), (620, 170, 25, "koopa"), (350, 130, 40, "goomba"), (550, 80, 40, "koopa")],
        coins_list=[(80, 510), (160, 460), (240, 410), (320, 360), (400, 310), (480, 260), (560, 210), (640, 160), (720, 110), (150, 170), (350, 120), (550, 70), (250, HEIGHT - 70), (500, HEIGHT - 70), (700, HEIGHT - 70)],
        flag_pos=(750, HEIGHT - 240), time_limit=120
    ),
]


# ============================================
# MAIN GAME FUNCTION
# ============================================
def main():
    """Main game function"""
    
    current_level = 0
    total_score = 0
    
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    bricks = pygame.sprite.Group()
    question_blocks = pygame.sprite.Group()
    power_ups = pygame.sprite.Group()
    
    player = Player(100, HEIGHT - 100)
    all_sprites.add(player)
    
    game_state = "menu"
    level_transition_timer = 0
    level_start_timer = 0
    
    def load_level(level_index):
        """Load a specific level"""
        all_sprites.empty()
        platforms.empty()
        enemies.empty()
        coins.empty()
        bricks.empty()
        question_blocks.empty()
        power_ups.empty()
        
        player.respawn()
        player.rect.x = 100
        player.rect.y = HEIGHT - 100
        player.start_x = 100
        player.start_y = HEIGHT - 100
        player.alive_status = True
        all_sprites.add(player)
        
        level = LEVELS[level_index]
        
        ground = Platform(0, HEIGHT - 40, WIDTH, 40, level.ground_color, is_ground=True)
        platforms.add(ground)
        all_sprites.add(ground)
        
        for plat_data in level.platforms_list:
            x, y, w, h, color, is_pipe = plat_data
            p = Platform(x, y, w, h, color, is_pipe)
            platforms.add(p)
            all_sprites.add(p)
        
        for brick_data in level.bricks_list:
            x, y, has_coin = brick_data
            b = Brick(x, y, has_coin)
            bricks.add(b)
            platforms.add(b)
            all_sprites.add(b)
        
        for qb_data in level.question_blocks_list:
            x, y, content = qb_data
            qb = QuestionBlock(x, y, content)
            question_blocks.add(qb)
            platforms.add(qb)
            all_sprites.add(qb)
        
        for enemy_data in level.enemies_list:
            x, y, patrol, enemy_type = enemy_data
            e = Enemy(x, y, patrol, enemy_type)
            enemies.add(e)
            all_sprites.add(e)
        
        for coin_pos in level.coins_list:
            x, y = coin_pos
            c = Coin(x, y)
            coins.add(c)
            all_sprites.add(c)
        
        flag = Flag(*level.flag_pos)
        all_sprites.add(flag)
        return level, flag
    
    level_transition_timer = 0
    level_start_timer = 180
    current_level_data, flag = load_level(0)
    
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        game_state = "menu"
                    else:
                        running = False
                if game_state == "menu":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game_state = "playing"
                        current_level = 0
                        total_score = 0
                        player.lives = 3
                        player.score = 0
                        player.alive_status = True
                        current_level_data, flag = load_level(0)
                        level_start_timer = 180
                if game_state == "game_over":
                    if event.key == pygame.K_r:
                        current_level = 0
                        total_score = 0
                        player.lives = 3
                        player.score = 0
                        player.alive_status = True
                        current_level_data, flag = load_level(0)
                        game_state = "playing"
                        level_start_timer = 180
                if game_state == "game_complete":
                    if event.key == pygame.K_r:
                        current_level = 0
                        total_score = 0
                        player.lives = 3
                        player.score = 0
                        player.alive_status = True
                        current_level_data, flag = load_level(0)
                        game_state = "playing"
                        level_start_timer = 180
        
        if game_state == "playing" or game_state == "level_complete":
            screen.fill(current_level_data.sky_color)
            
            if "Castle" in current_level_data.name or "Underground" in current_level_data.name:
                draw_stars()
            else:
                draw_clouds()
                draw_hills()
        else:
            screen.fill(SKY_BLUE)
            draw_clouds()
            draw_hills()
        
        if game_state == "menu":
            draw_text("SUPER MARIO BROS", huge_font, RED, WIDTH // 2, HEIGHT // 4)
            draw_text("Python Edition - 12 Stages!", medium_font, WHITE, WIDTH // 2, HEIGHT // 4 + 60)
            draw_text("Press ENTER or SPACE to Start", font, BLACK, WIDTH // 2, HEIGHT // 2)
            draw_text("Controls:", font, BLACK, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text("Arrow Keys / WASD - Move", font, BLACK, WIDTH // 2, HEIGHT // 2 + 80)
            draw_text("SPACE / UP / W - Jump", font, BLACK, WIDTH // 2, HEIGHT // 2 + 110)
            draw_text("Objective: Reach the flag in each stage!", font, BLACK, WIDTH // 2, HEIGHT // 2 + 150)
            draw_text(f"Total Stages: {len(LEVELS)}", font, MARIO_RED, WIDTH // 2, HEIGHT // 2 + 200)
            draw_text("Press ESC to quit", font, BLACK, WIDTH // 2, HEIGHT - 50)
        
        elif game_state == "playing":
            if level_start_timer > 0:
                level_start_timer -= 1
                all_sprites.draw(screen)
                
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                draw_text(current_level_data.name, large_font, WHITE, WIDTH // 2, HEIGHT // 2 - 30)
                draw_text(f"Stage {current_level_data.number} of {len(LEVELS)}", 
                         medium_font, YELLOW, WIDTH // 2, HEIGHT // 2 + 20)
                
                if level_start_timer < 60:
                    draw_text("Ready?", large_font, GREEN, WIDTH // 2, HEIGHT // 2 + 80)
                if level_start_timer < 30:
                    draw_text("GO!", large_font, RED, WIDTH // 2, HEIGHT // 2 + 80)
                
                draw_text(f"Score: {player.score + total_score}", font, WHITE, 20, 20, center=False)
                draw_text(f"Lives: {player.lives}", font, WHITE, WIDTH - 100, 20, center=False)
                
            else:
                if player.alive_status:
                    player.update(platforms)
                    enemies.update(platforms)
                    coins.update()
                    question_blocks.update()
                    
                    coin_collision = pygame.sprite.spritecollide(player, coins, False)
                    for coin in coin_collision:
                        if not coin.collected:
                            coin.collected = True
                            coin.kill()
                            player.score += 10
                    
                    qb_collision = pygame.sprite.spritecollide(player, question_blocks, False)
                    for qb in qb_collision:
                        if player.vel_y < 0 and player.rect.top < qb.rect.bottom and not qb.hit:
                            content = qb.hit_block()
                            if content == "coin":
                                player.score += 50
                                coin = Coin(qb.rect.x, qb.rect.y - 25)
                                coins.add(coin)
                                all_sprites.add(coin)
                            elif content == "power":
                                mush = PowerUp(qb.rect.x, qb.rect.y - 30)
                                power_ups.add(mush)
                                all_sprites.add(mush)
                                player.score += 100
                    
                    pu_collision = pygame.sprite.spritecollide(player, power_ups, True)
                    for pu in pu_collision:
                        player.lives += 1
                        player.score += 200
                    
                    enemy_collision = pygame.sprite.spritecollide(player, enemies, False)
                    for enemy in enemy_collision:
                        if player.vel_y > 0 and player.rect.bottom - 15 < enemy.rect.top:
                            enemy.kill()
                            player.stomp_bounce()
                            player.score += 50
                        elif player.invincible <= 0:
                            player.take_damage()
                            if player.lives <= 0:
                                game_state = "game_over"
                    
                    if player.rect.colliderect(flag.rect):
                        total_score += player.score
                        player.score = 0
                        
                        if current_level >= len(LEVELS) - 1:
                            game_state = "game_complete"
                        else:
                            current_level += 1
                            current_level_data, flag = load_level(current_level)
                            game_state = "level_complete"
                            level_transition_timer = 180
                
                all_sprites.draw(screen)
                
                draw_text(f"Score: {player.score + total_score}", font, WHITE, 20, 20, center=False)
                draw_text(f"Lives: {player.lives}", font, WHITE, WIDTH - 100, 20, center=False)
                draw_text(f"Stage: {current_level_data.number}/{len(LEVELS)}", 
                         font, WHITE, WIDTH // 2, 20, center=False)
                draw_text(f"x{player.score + total_score // 10}", font, YELLOW, 110, 20, center=False)
        
        elif game_state == "level_complete":
            all_sprites.draw(screen)
            level_transition_timer -= 1
            
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            if level_transition_timer > 60:
                draw_text(f"STAGE {current_level_data.number} CLEARED!", 
                         large_font, GREEN, WIDTH // 2, HEIGHT // 2 - 40)
                draw_text(f"Score: {player.score + total_score}", 
                         font, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            else:
                next_level = LEVELS[current_level]
                draw_text("NEXT STAGE:", medium_font, YELLOW, WIDTH // 2, HEIGHT // 2 - 60)
                draw_text(next_level.name, large_font, WHITE, WIDTH // 2, HEIGHT // 2)
            
            if level_transition_timer <= 0:
                game_state = "playing"
                level_start_timer = 180
        
        elif game_state == "game_over":
            all_sprites.draw(screen)
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("GAME OVER", huge_font, RED, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(f"Reached Stage: {current_level_data.number}", 
                     medium_font, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
            draw_text(f"Final Score: {total_score + player.score}", 
                     font, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text("Press R to Restart", font, YELLOW, WIDTH // 2, HEIGHT // 2 + 100)
            draw_text("Press ESC to Quit", font, WHITE, WIDTH // 2, HEIGHT // 2 + 140)
        
        elif game_state == "game_complete":
            screen.fill(SKY_BLUE)
            draw_clouds()
            draw_hills()
            
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            draw_text("CONGRATULATIONS!", huge_font, YELLOW, WIDTH // 2, HEIGHT // 4)
            draw_text("You completed all 12 stages!", medium_font, WHITE, WIDTH // 2, HEIGHT // 4 + 60)
            draw_text(f"Final Score: {total_score + player.score}", 
                     large_font, GREEN, WIDTH // 2, HEIGHT // 2)
            draw_text("Princess Peach is saved!", medium_font, PINK, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text("You are the ultimate Mario champion!", 
                     font, WHITE, WIDTH // 2, HEIGHT // 2 + 90)
            draw_text("Press R to Play Again", font, YELLOW, WIDTH // 2, HEIGHT - 100)
            draw_text("Press ESC to Quit", font, WHITE, WIDTH // 2, HEIGHT - 60)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
