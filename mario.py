import pygame
import sys

# Initialize pygame
pygame.init()

# ============================================
# GAME CONSTANTS
# ============================================
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
SKY_BLUE = (107, 140, 255)
GROUND_COLOR = (139, 69, 19)
PIPE_GREEN = (0, 168, 0)
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
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = 16
PLAYER_SPEED = 5

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros - Python Edition")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 48)


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


def draw_clouds():
    """Draw decorative clouds in the background"""
    cloud_positions = [(100, 60), (350, 40), (600, 80), (150, 120), (500, 100)]
    for x, y in cloud_positions:
        pygame.draw.circle(screen, WHITE, (x, y), 20)
        pygame.draw.circle(screen, WHITE, (x + 20, y), 25)
        pygame.draw.circle(screen, WHITE, (x + 40, y), 20)
        pygame.draw.rect(screen, WHITE, (x + 10, y - 5, 25, 20))


# ============================================
# SPRITE CLASSES
# ============================================
class Player(pygame.sprite.Sprite):
    """The Mario character"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = self.create_mario_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.invincible = 0
        self.alive_status = True
    
    def create_mario_sprite(self):
        """Create a Mario-like sprite using simple shapes"""
        surface = pygame.Surface((30, 40), pygame.SRCALPHA)
        # Hat (red)
        pygame.draw.rect(surface, MARIO_RED, (5, 0, 20, 8))
        pygame.draw.rect(surface, MARIO_RED, (0, 8, 25, 5))
        # Hat logo
        pygame.draw.rect(surface, WHITE, (10, 4, 10, 4))
        # Face (skin)
        pygame.draw.rect(surface, MARIO_SKIN, (5, 13, 20, 10))
        # Eyes
        pygame.draw.rect(surface, BLACK, (10, 16, 3, 3))
        pygame.draw.rect(surface, BLACK, (18, 16, 3, 3))
        # Mustache
        pygame.draw.rect(surface, MARIO_BROWN, (8, 21, 14, 2))
        # Body/Shirt (red)
        pygame.draw.rect(surface, MARIO_RED, (5, 23, 20, 8))
        # Overalls (blue)
        pygame.draw.rect(surface, MARIO_BLUE, (3, 31, 24, 9))
        # Buttons
        pygame.draw.circle(surface, YELLOW, (10, 35), 2)
        pygame.draw.circle(surface, YELLOW, (20, 35), 2)
        # Shoes (brown)
        pygame.draw.rect(surface, MARIO_BROWN, (3, 38, 10, 2))
        pygame.draw.rect(surface, MARIO_BROWN, (17, 38, 10, 2))
        return surface
    
    def update(self, platforms):
        """Update player position and handle collisions"""
        if not self.alive_status:
            return
            
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.on_ground = False
        
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Move horizontally and check collisions
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
        
        # Move vertically and check collisions
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
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        
        # Check if player fell off the screen
        if self.rect.top > HEIGHT:
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
            else:
                self.alive_status = False
        
        # Update invincibility frames
        if self.invincible > 0:
            self.invincible -= 1
            # Flashing effect
            if self.invincible % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    
    def respawn(self):
        """Respawn the player at starting position"""
        self.rect.x = 100
        self.rect.y = HEIGHT - 100
        self.vel_x = 0
        self.vel_y = 0
        self.invincible = 90
    
    def stomp_bounce(self):
        """Make player bounce after stomping enemy"""
        self.vel_y = -10


class Platform(pygame.sprite.Sprite):
    """Static platforms and ground"""
    
    def __init__(self, x, y, width, height, color=GROUND_COLOR, is_pipe=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        if is_pipe:
            # Draw pipe lip (darker green top)
            pygame.draw.rect(self.image, (0, 100, 0), (0, 0, width, 10))
            pygame.draw.rect(self.image, (50, 200, 50), (5, 0, width - 10, 5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_pipe = is_pipe


class Brick(pygame.sprite.Sprite):
    """Destructible brick blocks"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BRICK_COLOR)
        # Brick pattern
        pygame.draw.rect(self.image, BLACK, (0, 0, 40, 40), 2)
        pygame.draw.line(self.image, BLACK, (0, 20), (40, 20), 2)
        pygame.draw.line(self.image, BLACK, (20, 0), (20, 20), 2)
        pygame.draw.line(self.image, BLACK, (10, 20), (10, 40), 2)
        pygame.draw.line(self.image, BLACK, (30, 20), (30, 40), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit = False


class Enemy(pygame.sprite.Sprite):
    """Goomba enemies that patrol platforms"""
    
    def __init__(self, x, y, patrol_distance=200):
        super().__init__()
        self.image = self.create_goomba_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.vel_x = -1.5
        self.vel_y = 0
        self.on_ground = False
    
    def create_goomba_sprite(self):
        """Create a Goomba-like sprite"""
        surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (0, 8, 30, 22))
        # Head
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (5, 0, 20, 20))
        # Eyes
        pygame.draw.circle(surface, WHITE, (10, 8), 3)
        pygame.draw.circle(surface, WHITE, (20, 8), 3)
        pygame.draw.circle(surface, BLACK, (10, 8), 1)
        pygame.draw.circle(surface, BLACK, (20, 8), 1)
        # Eyebrows (angry)
        pygame.draw.rect(surface, BLACK, (7, 4, 6, 2))
        pygame.draw.rect(surface, BLACK, (17, 4, 6, 2))
        # Feet
        pygame.draw.ellipse(surface, (100, 50, 0), (0, 25, 12, 8))
        pygame.draw.ellipse(surface, (100, 50, 0), (18, 25, 12, 8))
        return surface
    
    def update(self, platforms):
        """Update enemy position and patrol behavior"""
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Move horizontally
        self.rect.x += self.vel_x
        
        # Check horizontal collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = -abs(self.vel_x)
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = abs(self.vel_x)
        
        # Move vertically
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
        
        # Patrol behavior - turn around after traveling patrol distance
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


class Flag(pygame.sprite.Sprite):
    """The goal/flag to reach"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = self.create_flag_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def create_flag_sprite(self):
        """Create the flag pole and flag"""
        surface = pygame.Surface((40, 200), pygame.SRCALPHA)
        # Pole
        pygame.draw.rect(surface, (200, 200, 200), (18, 0, 4, 200))
        # Flag
        pygame.draw.polygon(surface, GREEN, [(22, 20), (40, 30), (22, 40)])
        # Ball on top
        pygame.draw.circle(surface, (255, 215, 0), (20, 5), 5)
        return surface


# ============================================
# MAIN GAME FUNCTION
# ============================================
def main():
    """Main game function"""
    
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    
    # Create player
    player = Player(100, HEIGHT - 100)
    all_sprites.add(player)
    
    # Create ground
    ground = Platform(0, HEIGHT - 40, WIDTH, 40, GROUND_COLOR)
    platforms.add(ground)
    all_sprites.add(ground)
    
    # Add grass on top of ground
    for x in range(0, WIDTH, 40):
        grass = Platform(x, HEIGHT - 45, 40, 5, GREEN)
        platforms.add(grass)
        all_sprites.add(grass)
    
    # Create floating platforms
    platform1 = Platform(200, 450, 150, 20)
    platform2 = Platform(450, 350, 150, 20)
    platform3 = Platform(100, 280, 100, 20)
    platform4 = Platform(600, 400, 120, 20)
    platform5 = Platform(350, 200, 100, 20)
    platforms.add(platform1, platform2, platform3, platform4, platform5)
    all_sprites.add(platform1, platform2, platform3, platform4, platform5)
    
    # Create pipes (classic Mario element)
    pipe1 = Platform(300, HEIGHT - 90, 60, 50, PIPE_GREEN, is_pipe=True)
    pipe2 = Platform(550, HEIGHT - 120, 60, 80, PIPE_GREEN, is_pipe=True)
    platforms.add(pipe1, pipe2)
    all_sprites.add(pipe1, pipe2)
    
    # Create brick blocks
    brick_positions = [(350, 450), (390, 450), (430, 450), (250, 200), (290, 200)]
    for pos in brick_positions:
        brick = Brick(*pos)
        platforms.add(brick)
        all_sprites.add(brick)
    
    # Create enemies (Goombas)
    enemy1 = Enemy(400, HEIGHT - 70, patrol_distance=150)
    enemy2 = Enemy(650, HEIGHT - 70, patrol_distance=100)
    enemy3 = Enemy(250, HEIGHT - 70, patrol_distance=120)
    enemies.add(enemy1, enemy2, enemy3)
    all_sprites.add(enemy1, enemy2, enemy3)
    
    # Create coins
    coin_positions = [
        (250, 420), (500, 320), (130, 250), (650, 370),
        (300, HEIGHT - 70), (700, HEIGHT - 70), (365, 420),
        (270, 170), (500, 280), (600, 200)
    ]
    for pos in coin_positions:
        coin = Coin(*pos)
        coins.add(coin)
        all_sprites.add(coin)
    
    # Create flag (goal)
    flag = Flag(750, HEIGHT - 240)
    all_sprites.add(flag)
    
    # Game state
    game_state = "menu"  # menu, playing, game_over, win
    
    # ============================================
    # GAME LOOP
    # ============================================
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
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
                if game_state in ["game_over", "win"]:
                    if event.key == pygame.K_r:
                        main()  # Restart the game
                        return
        
        # Draw background
        screen.fill(SKY_BLUE)
        draw_clouds()
        
        # ============================================
        # GAME STATE: MENU
        # ============================================
        if game_state == "menu":
            draw_text("SUPER MARIO BROS", large_font, RED, WIDTH // 2, HEIGHT // 4)
            draw_text("Python Edition", font, WHITE, WIDTH // 2, HEIGHT // 4 + 50)
            draw_text("Press ENTER or SPACE to Start", font, BLACK, WIDTH // 2, HEIGHT // 2)
            draw_text("Controls:", font, BLACK, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text("Arrow Keys / WASD - Move", font, BLACK, WIDTH // 2, HEIGHT // 2 + 80)
            draw_text("SPACE / UP / W - Jump", font, BLACK, WIDTH // 2, HEIGHT // 2 + 110)
            draw_text("Objective: Collect coins and reach the flag!", font, BLACK, WIDTH // 2, HEIGHT // 2 + 150)
            draw_text("Press ESC to quit", font, BLACK, WIDTH // 2, HEIGHT - 50)
        
        # ============================================
        # GAME STATE: PLAYING
        # ============================================
        elif game_state == "playing":
            # Update player
            if player.alive_status:
                player.update(platforms)
                enemies.update(platforms)
                coins.update()
                
                # Check coin collisions
                coin_collision = pygame.sprite.spritecollide(player, coins, False)
                for coin in coin_collision:
                    if not coin.collected:
                        coin.collected = True
                        coin.kill()
                        player.score += 10
                
                # Check enemy collisions
                enemy_collision = pygame.sprite.spritecollide(player, enemies, False)
                for enemy in enemy_collision:
                    # Check if player is jumping on enemy (stomp)
                    if player.vel_y > 0 and player.rect.bottom - 10 < enemy.rect.top:
                        enemy.kill()
                        player.stomp_bounce()
                        player.score += 50
                    elif player.invincible <= 0:
                        # Player takes damage
                        player.lives -= 1
                        player.invincible = 90
                        if player.lives <= 0:
                            player.alive_status = False
                            game_state = "game_over"
                        else:
                            player.respawn()
                
                # Check flag collision (win condition)
                if player.rect.colliderect(flag.rect):
                    game_state = "win"
            
            # Draw all sprites
            all_sprites.draw(screen)
            
            # Draw HUD
            draw_text(f"Score: {player.score}", font, WHITE, 20, 20, center=False)
            draw_text(f"Lives: {player.lives}", font, WHITE, WIDTH - 100, 20, center=False)
            draw_text(f"x{player.score // 10}", font, YELLOW, 100, 20, center=False)
        
        # ============================================
        # GAME STATE: GAME OVER
        # ============================================
        elif game_state == "game_over":
            all_sprites.draw(screen)
            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("GAME OVER", large_font, RED, WIDTH // 2, HEIGHT // 2 - 40)
            draw_text(f"Final Score: {player.score}", font, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text("Press R to Restart", font, WHITE, WIDTH // 2, HEIGHT // 2 + 60)
            draw_text("Press ESC to Quit", font, WHITE, WIDTH // 2, HEIGHT // 2 + 100)
        
        # ============================================
        # GAME STATE: WIN
        # ============================================
        elif game_state == "win":
            all_sprites.draw(screen)
            # Celebration overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("YOU WIN!", large_font, YELLOW, WIDTH // 2, HEIGHT // 2 - 40)
            draw_text(f"Final Score: {player.score}", font, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text("Princess is saved!", font, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text("Press R to Play Again", font, WHITE, WIDTH // 2, HEIGHT // 2 + 90)
            draw_text("Press ESC to Quit", font, WHITE, WIDTH // 2, HEIGHT // 2 + 130)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


# ============================================
# RUN THE GAME
# ============================================
if __name__ == "__main__":
    main()
