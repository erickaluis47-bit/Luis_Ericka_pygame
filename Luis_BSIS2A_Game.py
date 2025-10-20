import pygame
import math
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PURPLE = (138, 43, 226)
PINK = (255, 20, 147)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT_PURPLE = (221, 160, 221)
DARK_PINK = (199, 21, 133)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aurora Bubble Ascent - Start Fixed")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)

# Background aurora waves
wave_amplitude = 50
wave_frequency = 0.02
wave_speed = 1

# Player bubble
player_x = SCREEN_WIDTH // 2 + 50  # Slightly offset to avoid any init overlap
player_y = SCREEN_HEIGHT // 2
player_size = 25
player_velocity_y = 0
player_velocity_x = 0
gravity = 0.3
boost = -7
horizontal_speed = 3
boost_timer = 0

# Game state
game_started = False  # NEW: Prevents logic until start
game_start_time = 0  # Will be set on start
elapsed_time = 0
score = 0
height_reached = 0
lives = 4  # More forgiving
game_duration = 120000  # 2 minutes
game_over = False
running = True

# Collectibles and obstacles (initialized but paused)
stars = []
star_cycle = 0
star_positions = [
    (200, 150), (400, 250), (600, 100), (300, 350), (500, 200),
    (150, 450), (450, 300), (650, 400), (250, 500), (550, 300)
]
for i in range(10):
    stars.append({
        'x': star_positions[i][0],
        'y': star_positions[i][1] + (i * 50),
        'collected': False,
        'cycle_offset': i * 100
    })

clouds = []
cloud_positions = [
    (250, 500), (450, 450), (600, 550), (350, 400), (550, 350),
    (200, 250), (400, 300), (700, 200), (300, 150), (500, 100)
]
for i in range(10):
    clouds.append({
        'x': cloud_positions[i][0],
        'y': cloud_positions[i][1] + (i * 30),
        'size': 35 + (i % 3) * 10,
        'cycle_offset': i * 150
    })

def draw_aurora_background(elapsed_time_val):
    """Helper to draw background (works even before start)"""
    for x in range(0, SCREEN_WIDTH, 5):
        for wave in range(3):
            y_offset = wave_amplitude * math.sin(wave_frequency * x + wave + elapsed_time_val * 0.001 * wave_speed)
            color_intensity = 255 - wave * 50
            color = (138, color_intensity // 2, 226)
            pygame.draw.line(screen, color, (x, 0), (x, SCREEN_HEIGHT), 5)
            pygame.draw.line(screen, (255, 20 + wave * 50, 147), (x, y_offset + SCREEN_HEIGHT // 2), (x, SCREEN_HEIGHT), 3)

while running:
    current_time = pygame.time.get_ticks()
    
    # Draw background always
    draw_aurora_background(current_time)  # Use current_time for animation even pre-start
    
    keys = pygame.key.get_pressed()
    
    if not game_started:
        # Start screen logic
        player_velocity_x = 0
        player_velocity_y = 0  # No movement
        player_x = SCREEN_WIDTH // 2 + 50
        player_y = SCREEN_HEIGHT // 2
        
        # Draw pulsing bubble on start screen
        pulse = math.sin(current_time * 0.01) * 3
        glow_size = player_size + int(pulse)
        pygame.draw.circle(screen, LIGHT_PURPLE, (int(player_x), int(player_y)), glow_size)
        pygame.draw.circle(screen, PINK, (int(player_x), int(player_y)), player_size)
        pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), player_size // 3)
        
        # Start screen text
        title_text = font.render("Aurora Bubble Ascent", True, WHITE)
        start_text = font.render("Press Space or Up to Begin!", True, GOLD)
        controls_text = small_font.render("Arrows/A-D: Move | Space/Up: Boost | Collect Stars, Dodge Clouds", True, WHITE)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 30))
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 + 20))
        
        # Check for start input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    game_started = True
                    game_start_time = current_time  # Start timer now
                    player_velocity_y = boost  # Initial boost for fun start
                    boost_timer = 30
        pygame.display.flip()
        clock.tick(FPS)
        continue  # Skip rest of loop until started
    
    # Game logic only after start
    elapsed_time = current_time - game_start_time
    time_left = max(0, (game_duration - elapsed_time) // 1000)
    
    # Player input
    player_velocity_x = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_velocity_x = -horizontal_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_velocity_x = horizontal_speed
    
    if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and player_y > 0:
        if player_velocity_y > -2:
            player_velocity_y = boost
            boost_timer = max(boost_timer, 30)
    
    # Physics
    player_velocity_y += gravity
    player_y += player_velocity_y
    player_x += player_velocity_x
    
    # Boundaries
    player_x = max(player_size, min(SCREEN_WIDTH - player_size, player_x))
    player_y = max(0, min(SCREEN_HEIGHT - player_size, player_y))
    
    # Ground/height
    if player_y >= SCREEN_HEIGHT - player_size:
        player_y = SCREEN_HEIGHT - player_size
        player_velocity_y = 0
    height_reached = max(height_reached, SCREEN_HEIGHT - player_y)
    
    # Cycle elements
    star_cycle += 2
    for star in stars:
        star['y'] += 2
        if star['y'] > SCREEN_HEIGHT + 50:
            star['y'] = -50 + (star_cycle + star['cycle_offset']) % 600
        if not star['collected']:
            dist = math.sqrt((player_x - star['x']) ** 2 + (player_y - star['y']) ** 2)
            if dist < player_size + 15:
                star['collected'] = True
                score += 50
                boost_timer = 60
                lives += 1
    
    cloud_cycle = star_cycle
    for cloud in clouds:
        cloud['y'] += 2.5
        if cloud['y'] > SCREEN_HEIGHT + 50:
            cloud['y'] = -50 + (cloud_cycle + cloud['cycle_offset']) % 700
        if boost_timer <= 0 and lives > 0:  # Prevent init drop to 0
            dist = math.sqrt((player_x - cloud['x']) ** 2 + (player_y - cloud['y']) ** 2)
            if dist < player_size + cloud['size'] // 2:
                lives -= 1
                boost_timer = 30
                if lives <= 0:
                    game_over = True
        else:
            if boost_timer > 0:
                boost_timer -= 1
    
    if elapsed_time >= game_duration:
        game_over = True
    
    # Draw player
    pulse = math.sin(elapsed_time * 0.01) * 3
    glow_size = player_size + int(pulse)
    pygame.draw.circle(screen, LIGHT_PURPLE, (int(player_x), int(player_y)), glow_size)
    pygame.draw.circle(screen, PINK, (int(player_x), int(player_y)), player_size)
    pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), player_size // 3)
    
    # Draw stars and clouds
    for star in stars:
        if not star['collected']:
            star_glow = math.sin(elapsed_time * 0.005 + star['x']) * 5
            pygame.draw.circle(screen, GOLD, (int(star['x']), int(star['y'])), 10 + int(star_glow))
            pygame.draw.circle(screen, WHITE, (int(star['x']), int(star['y'])), 3)
    
    for cloud in clouds:
        pygame.draw.circle(screen, DARK_PINK, (int(cloud['x']), int(cloud['y'])), cloud['size'])
        pygame.draw.circle(screen, BLACK, (int(cloud['x'] + 10), int(cloud['y'] - 5)), cloud['size'] // 2)
    
    # Events (after start)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                # Restart (resets to start screen)
                game_started = False
                score = 0
                height_reached = 0
                lives = 4
                player_x = SCREEN_WIDTH // 2 + 50
                player_y = SCREEN_HEIGHT // 2
                player_velocity_y = 0
                player_velocity_x = 0
                star_cycle = 0
                for i, star in enumerate(stars):
                    star['collected'] = False
                    star['y'] = star_positions[i][1]
                for i, cloud in enumerate(clouds):
                    cloud['y'] = cloud_positions[i][1]
                boost_timer = 0
                game_over = False
    
    # UI (only during game)
    if game_started and not game_over:
        score_text = font.render(f"Score: {score}", True, WHITE)
        height_text = small_font.render(f"Height: {height_reached}", True, WHITE)
        lives_text = small_font.render(f"Lives: {lives}", True, WHITE)
        time_text = small_font.render(f"Time: {time_left}s", True, WHITE)
        
        screen.blit(score_text, (20, 20))
        screen.blit(height_text, (20, 70))
        screen.blit(lives_text, (20, 100))
        screen.blit(time_text, (20, 130))
    
    # Game over overlay (only after actual play)
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        if lives > 0 and score > 500:
            msg = font.render("Ascension Complete!", True, GOLD)
        else:
            msg = font.render("Bubble Burst!", True, PINK)
        final_score = font.render(f"Final Score: {score} | Max Height: {height_reached}", True, WHITE)
        restart_text = small_font.render("Press R to restart or ESC to quit", True, WHITE)
        controls_tip = small_font.render("Use Arrows/A-D to move, Space/Up to boost!", True, WHITE)
        
        screen.blit(msg, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 80))
        screen.blit(final_score, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 20))
        screen.blit(controls_tip, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()