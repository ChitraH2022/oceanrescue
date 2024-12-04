import math
import random
import pygame
from pygame import mixer

# Initialize pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((1024, 750))

# Background
background = pygame.image.load('background2.png')
background = pygame.transform.scale(background, (1024, 750))

# Sound
mixer.music.load("underwaterSound.wav")
mixer.music.play(-1)  # Loop background music

# Shooting sound
shoot_sound = mixer.Sound("bubbleshot.wav")  # Load shooting sound

# Caption and Icon
pygame.display.set_caption("Ocean Cleanup")
icon = pygame.image.load('spaceship.png')
pygame.display.set_icon(icon)

# Player (octopus)
playerImg = pygame.image.load('octopus.png')
playerX = 150
playerY = 600  # Keep it at the bottom of the screen
playerX_change = 0  # Initially no movement on X-axis

# Plastic Objects - 6 types (falling from above)
plastic_images = [
    pygame.image.load('pipe.png'),
    pygame.image.load('bottle.png'),
    pygame.image.load('bag.png'),
    pygame.image.load('fishingnets.png'),
    pygame.image.load('can.png'),
    pygame.image.load('straw.png')
]
plastic_types = ["Pipes", "Bottles", "Bags", "Nets", "Cans", "Straws"]
plastic_positions = [{'x': random.randint(100, 600), 'y': -50} for _ in range(6)]
plastic_speed = 0.2
plastic_visibility = [False] * 6
plastic_spawn_timers = [pygame.time.get_ticks()] * 6
spawn_interval = 4000  # Interval for each plastic spawn (3 seconds)

# Fish Objects - 3 types (moving left to right)
fish_images = [
    pygame.image.load('seaturtle.png'),
    pygame.image.load('clownfish.png'),
    pygame.image.load('fish2.png')
]
fish_positions = [{'x': random.randint(-100, -50), 'y': random.randint(200, 400)} for _ in range(3)]
fish_speed = 0.5
fish_direction = [1 for _ in range(3)]

# Bullet (bubble)
bulletImg = pygame.image.load('bubble2.png')
bulletX = []
bulletY = []
bulletX_change = 0
bulletY_change = 5
bullet_state = []

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# Timer
start_ticks = pygame.time.get_ticks()

# Plastic Counter
plastic_count = {plastic: 0 for plastic in plastic_types}

# Define points for each plastic type
plastic_points = {
    "Pipes": 1,
    "Bottles": 1,
    "Bags": 2,
    "Nets": 1,
    "Cans": 1,
    "Straws": 1
}

# Define penalties for shooting fish/turtle
fish_penalty = 5


# Function to display the start screen
def start_screen():
    screen.fill((25, 25, 176))  # Background color for the start screen
    title_font = pygame.font.Font('freesansbold.ttf', 64)
    info_font = pygame.font.Font('freesansbold.ttf', 32)

    title_text = title_font.render("Ocean Cleanup", True, (255, 255, 255))
    info_text = info_font.render("Press ENTER to start", True, (255, 255, 255))

    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 250))
    screen.blit(info_text, (screen.get_width() // 2 - info_text.get_width() // 2, 350))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False


# Function to display the score
def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


# Function to display the timer
def show_timer(x, y, time_left):
    timer_font = pygame.font.Font('freesansbold.ttf', 32)
    timer = timer_font.render(f"Time Left: {time_left}s", True, (255, 255, 255))
    screen.blit(timer, (x, y))


# Function to display the plastic count
def show_plastic_count(x, y):
    small_font = pygame.font.Font('freesansbold.ttf', 20)
    y_offset = 30
    for i, plastic in enumerate(plastic_types):
        count_text = small_font.render(f"{plastic}: {plastic_count[plastic]}", True, (255, 255, 255))
        screen.blit(count_text, (x + i * 150, y))


def player(x, y):
    screen.blit(playerImg, (x, y))


def fire_bullet(x, y):
    screen.blit(bulletImg, (x + 20, y - 10))


def isCollision(plasticX, plasticY, bulletX, bulletY):
    distance = math.sqrt(math.pow(plasticX - bulletX, 2) + (math.pow(plasticY - bulletY, 2)))
    return distance < 27


def isFishCollision(fishX, fishY, bulletX, bulletY):
    distance = math.sqrt(math.pow(fishX - bulletX, 2) + (math.pow(fishY - bulletY, 2)))
    return distance < 27


def display_end_message():
    end_font = pygame.font.Font('freesansbold.ttf', 32)
    end_message = end_font.render("Game Over! Thanks for playing!", True, (255, 255, 255))
    screen.blit(end_message, (screen.get_width() // 2 - end_message.get_width() // 2, 300))
    pygame.display.update()


# Display the start screen
start_screen()


# Game Loop
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    # Calculate remaining time
    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(60 - seconds_passed, 0)

    if time_left == 0:  # Game ends when time runs out
        display_end_message()
        pygame.time.delay(3000)  # Wait for 3 seconds before closing
        break  # Exit the game loop

    # Show timer
    show_timer(800, 10, time_left)

    # Spawn plastics independently
    for i in range(len(plastic_visibility)):
        if pygame.time.get_ticks() - plastic_spawn_timers[i] >= random.randint(2000, 5000):
            if not plastic_visibility[i]:
                plastic_visibility[i] = True
                plastic_positions[i]['x'] = random.randint(100, 600)
                plastic_positions[i]['y'] = -50
                plastic_spawn_timers[i] = pygame.time.get_ticks()

    # Move plastics downward
    for i in range(len(plastic_images)):
        if plastic_visibility[i]:
            plastic_positions[i]['y'] += plastic_speed
            if plastic_positions[i]['y'] > screen.get_height():
                plastic_visibility[i] = False

            for j in range(len(bulletX)):
                if bullet_state[j] == "fire":
                    fire_bullet(bulletX[j], bulletY[j])
                    bulletY[j] -= bulletY_change
                    collision = isCollision(plastic_positions[i]['x'], plastic_positions[i]['y'], bulletX[j], bulletY[j])
                    if collision:
                        bullet_state[j] = "ready"
                        bulletY[j] = playerY
                        score_value += plastic_points[plastic_types[i]]
                        plastic_count[plastic_types[i]] += 1
                        plastic_visibility[i] = False

    # Move fish
    for i in range(len(fish_positions)):
        fish_positions[i]['x'] += fish_speed * fish_direction[i]
        if fish_positions[i]['x'] > screen.get_width():
            fish_positions[i]['x'] = -50
            fish_positions[i]['y'] = random.randint(350, 650)

        for j in range(len(bulletX)):
            if bullet_state[j] == "fire":
                collision_with_fish = isFishCollision(fish_positions[i]['x'], fish_positions[i]['y'], bulletX[j], bulletY[j])
                if collision_with_fish:
                    bullet_state[j] = "ready"
                    bulletY[j] = playerY
                    score_value -= fish_penalty  # Deduct points for shooting fish/turtle

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle player movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -2
            if event.key == pygame.K_RIGHT:
                playerX_change = 2
            if event.key == pygame.K_SPACE:
                bulletX.append(playerX)
                bulletY.append(playerY)
                bullet_state.append("fire")
                shoot_sound.play()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Update player position
    playerX += playerX_change
    playerX = max(0, min(playerX, screen.get_width() - playerImg.get_width()))

    # Draw player, plastics, fish, score, timer, and plastic counts
    player(playerX, playerY)
    for i in range(len(plastic_images)):
        if plastic_visibility[i]:
            screen.blit(plastic_images[i], (plastic_positions[i]['x'], plastic_positions[i]['y']))

    for i in range(len(fish_images)):
        screen.blit(fish_images[i], (fish_positions[i]['x'], fish_positions[i]['y']))

    show_score(textX, textY)
    show_plastic_count(textX, textY + 40)

    pygame.display.update()
