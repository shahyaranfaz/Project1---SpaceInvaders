import math
import pygame

# Screen size constants
pygame.init()
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
FONT_25 = pygame.font.Font("assets/fonts/text_font.ttf", 25)
FONT_40 = pygame.font.Font("assets/fonts/text_font.ttf", 40)
FONT_50 = pygame.font.Font("assets/fonts/text_font.ttf", 50)
FONT_60 = pygame.font.Font("assets/fonts/text_font.ttf", 60)
FONT_85 = pygame.font.Font("assets/fonts/text_font.ttf", 85)
FONT_100 = pygame.font.Font("assets/fonts/text_font.ttf", 100)
FONT_LOGO = pygame.font.Font("assets/fonts/logo_font.ttf", 100)

# Player movement constants
PLAYER_SPEED = 6
SCORE_PER_KILL = 3
AMMO_PER_KILL = 3
ENEMY_SPEED = 3
BULLET_SPEED = 15
DIRECTIONS = ["L", "R", "U", "D", "LU", "RU", "LD", "RD"]
USER_INPUTS = {
    # L  R  U  D
    (1, 1, 1, 1): (None, None),
    (1, 1, 1, 0): ("U", pygame.image.load("assets/character_icons/spaceship_up.png")),
    (1, 1, 0, 1): ("D", pygame.image.load("assets/character_icons/spaceship_down.png")),
    (1, 1, 0, 0): (None, None),
    (1, 0, 1, 1): ("L", pygame.image.load("assets/character_icons/spaceship_left.png")),
    (1, 0, 1, 0): ("LU", pygame.image.load("assets/character_icons/spaceship_left_up.png")),
    (1, 0, 0, 1): ("LD", pygame.image.load("assets/character_icons/spaceship_left_down.png")),
    (1, 0, 0, 0): ("L", pygame.image.load("assets/character_icons/spaceship_left.png")),
    (0, 1, 1, 1): ("R", pygame.image.load("assets/character_icons/spaceship_right.png")),
    (0, 1, 1, 0): ("RU", pygame.image.load("assets/character_icons/spaceship_right_up.png")),
    (0, 1, 0, 1): ("RD", pygame.image.load("assets/character_icons/spaceship_right_down.png")),
    (0, 1, 0, 0): ("R", pygame.image.load("assets/character_icons/spaceship_right.png")),
    (0, 0, 1, 1): (None, None),
    (0, 0, 1, 0): ("U", pygame.image.load("assets/character_icons/spaceship_up.png")),
    (0, 0, 0, 1): ("D", pygame.image.load("assets/character_icons/spaceship_down.png")),
    (0, 0, 0, 0): (None, None)
}
SHOOTING_OFFSETS = {
    "RU": (21, 24),
    "LU": (24, 24),
    "LD": (24, 21),
    "RD": (21, 21)
}
SHOOTING_COOLDOWN = 300
MOVEMENT_COEFFICIENTS = {
    "L": (-1, 0),
    "R": (1, 0),
    "U": (0, -1),
    "D": (0, 1),
    "LU": (-1 / math.sqrt(2), -1 / math.sqrt(2)),
    "RU": (1 / math.sqrt(2), -1 / math.sqrt(2)),
    "LD": (-1 / math.sqrt(2), 1 / math.sqrt(2)),
    "RD": (1 / math.sqrt(2), 1 / math.sqrt(2))
}
ENEMY_SPAWN_RATES = {
    0: 3,
    10: 5,
    20: 7,
    100: 10,
    500: 20,
    1000: 50,
    5000: 100,
    10000: 150
}

AMMO_COLOURS = {
    0: (255, 0, 0),
    999: (0, 255, 0)
}

KEY_STROKES = {
    pygame.K_LEFT: "L",
    pygame.K_RIGHT: "R",
    pygame.K_UP: "U",
    pygame.K_DOWN: "D"
}

OPPOSITE_DIRECTIONS = {
    "L": ["R", "RU", "RD"],
    "R": ["L", "LU", "LD"],
    "U": ["D", "LD", "RD"],
    "D": ["U", "LU", "RU"],
    "LU": ["RD"],
    "LD": ["RU"],
    "RU": ["LD"],
    "RD": ["LU"]
}
