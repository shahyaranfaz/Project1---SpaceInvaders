from __future__ import annotations
from random import randint, choice
from game_token import (ScoreToken, AmmoToken, PowerUpToken, PUPiercingAmmo,
                        PUDoubleScore, PUDoubleMovementSpeed,
                        PUSDoubleShootingSpeed)
from constants import *
from abc import ABC, abstractmethod

class Character(ABC):
    """Abstract base class for user and enemy characters.

    Attributes:
        - image (pygame.Surface): Visual representation of character.
        - x (float): The x-coordinate of the character.
        - y (float): The y-coordinate of the character.
        - rect (pygame.Rect): The rectangular area that defines the position
          and size of the character.
    """
    image: pygame.Surface
    x: float
    y: float
    rect: pygame.Rect

    def __init__(self, x: float, y: float, image: str) -> None:
        """Initialize a character with a visual of <image> at <x>, <y>.

        This is an abstract class and should not be instantiated directly.
        """
        self.image = pygame.image.load(image)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw <self> on <screen>."""
        screen.blit(self.image, self.rect)

    @abstractmethod
    def update(self) -> None:
        """Update <self>'s position."""
        raise NotImplementedError

    def move(self, distance: tuple[int, int], speed: int) -> str:
        """Move <self> by <distance> scaled by <speed> and return boundary hit."""
        self.x += distance[0] * speed
        self.y += distance[1] * speed

        hitting_boundary = ""
        if self.x < 0:
            self.x = 0
            hitting_boundary = "L"
        elif self.x + self.rect.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.rect.width
            hitting_boundary = "R"
        if self.y < 0:
            self.y = 0
            hitting_boundary += "U"
        elif self.y + self.rect.height > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.rect.height
            hitting_boundary += "D"

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        return hitting_boundary

    def place(self, screen) -> None:
        """Update <self>'s location and draw on <screen>."""
        self.update()
        self.draw(screen)


class UserPlayer(Character):
    """The user's character.

    Attributes:
        - user_input (dict[str, int]): Tracks the user's directional inputs.
        - direction (str): The direction of player's current movement.
        - shooting (bool): Whether the player is currently shooting.
        - score (int): The player's score.
        - kills (int): The player's kills.
        - max_enemies (int): The number of enemies currently generating.
        - bullets (list[Bullet]): The bullets fired by player.
        - ammo (int): The number of bullets the player has left.
        - last_shot_time (float): The last time the player fired a bullet.
        - last_score_time (float): The last time the player received a score.
        - power_up (PowerUpToken/None): The player's power-up.
    """
    user_input: dict[str, int]
    direction: str
    shooting: bool
    score: int
    kills: int
    max_enemies: int
    bullets: list[Bullet]
    ammo: int
    last_shot_time: float
    last_score_time: float
    power_up: Optional[PowerUpToken]
    def __init__(self, x: float, y: float) -> None:
        """Initialize a player at <x>, <y>."""
        super().__init__(x, y, "assets/character_icons/spaceship_up.png")
        self.user_input = {"L": 0, "R": 0, "U": 0, "D": 0}
        self.direction = "U"
        self.shooting = False
        self.score = 0
        self.kills = 0
        self.max_enemies = ENEMY_SPAWN_RATES[0]
        self.bullets = []
        self.ammo = 10
        self.last_shot_time = 0
        self.last_score_time = 0
        self.power_up = None

    def update(self) -> None:
        """Update <self>'s state based on input and power-ups."""
        input_ = tuple(self.user_input.values())
        if USER_INPUTS[input_][0]:
            self.direction = USER_INPUTS[input_][0]
            self.image = USER_INPUTS[input_][1]
            if str(self.power_up) == "DoubleMovementSpeed":
                self.move(MOVEMENT_COEFFICIENTS[self.direction], PLAYER_SPEED * 2)
            else:
                self.move(MOVEMENT_COEFFICIENTS[self.direction], PLAYER_SPEED)

    def shoot(self) -> None:
        """Fire a bullet if ammo and cooldown allow."""
        if self.ammo == 0:
            return None
        time_since_last = pygame.time.get_ticks() - self.last_shot_time
        if time_since_last >= SHOOTING_COOLDOWN or str(self.power_up) == "DoubleShootingSpeed" and time_since_last >= SHOOTING_COOLDOWN // 2:
            if len(self.direction) == 1:
                x = self.rect.center[0]
                y = self.rect.center[1]
            else:
                x = self.rect.topleft[0] + SHOOTING_OFFSETS[self.direction][0]
                y = self.rect.topleft[1] + SHOOTING_OFFSETS[self.direction][1]
            self.bullets.append(Bullet(x, y, self.direction))
            self.last_shot_time = pygame.time.get_ticks()
            self.ammo -= 1

    def update_bullets(self) -> None:
        """Remove bullets that leave the screen."""
        self.bullets = [bullet for bullet in self.bullets
                        if 0 <= bullet.x <= SCREEN_WIDTH and
                        0 <= bullet.y <= SCREEN_HEIGHT]

    def away_from_player(self) -> tuple[int, int]:
        """Return a random location at least 100px away from <self>."""
        def get_coord(pos, max_value):
            if pos < 50:
                return randint(pos, max_value)
            elif pos > max_value - 50:
                return randint(50, pos)
            else:
                return randint(50, pos) if randint(0, 1) else randint(pos, max_value)

        while True:
            new_x = get_coord(self.rect.x, SCREEN_WIDTH - 50)
            new_y = get_coord(self.rect.y, SCREEN_HEIGHT - 50)

            if abs(new_x - self.rect.x) >= 100 or abs(new_y - self.rect.y) >= 100:
                return new_x, new_y


    def check_for_kills(self, enemies) -> None:
        """Check bullet collisions with enemies in <enemies> and update
        <self>'s stats.
        """
        kills = 0
        for bullet in self.bullets.copy():
            x = bullet.check_for_enemies(enemies)
            if x != 0 and str(self.power_up) != "PiercingAmmo":
                self.bullets.remove(bullet)
            kills += x
        self.add_kills(kills)
        self.add_score(SCORE_PER_KILL * kills)
        self.add_ammo(AMMO_PER_KILL * kills)

    def set_enemy_count(self, enemies: list[Enemy]) -> None:
        """Adjust enemy count to match current spawn rate."""
        self.max_enemies = ENEMY_SPAWN_RATES.get(self.kills, self.max_enemies)
        while len(enemies) < self.max_enemies:
            enemies.append(Enemy(self.away_from_player()))

    def update_score(self) -> None:
        """Increment score once per second."""
        time_since_last = pygame.time.get_ticks() - self.last_score_time
        if time_since_last >= 1000:
            self.add_score(1)
            self.last_score_time = pygame.time.get_ticks()

    def update_tokens(self, tokens) -> None:
        """Possibly spawn tokens and handle power-up expiration."""
        location = self.away_from_player()
        if randint(1, 1000) == 1:
            tokens.append(ScoreToken(location))
        elif randint(1, 250) == 1:
            tokens.append(AmmoToken(location))
        else:
            rand = randint(1, 5000)
            if rand == 1:
                tokens.append(PUSDoubleShootingSpeed(location))
            elif rand == 2:
                tokens.append(PUDoubleMovementSpeed(location))
            elif rand == 3:
                tokens.append(PUDoubleScore(location))
            elif rand == 4:
                tokens.append(PUPiercingAmmo(location))

        if self.power_up is not None and self.power_up.check_for_completion():
            self.set_power_up(None)

    def set_power_up(self, power_up) -> None:
        """Assign a new power-up to <self>."""
        self.power_up = power_up

    def set_user_input(self, event_key, event_value) -> None:
        """Update stored user input for given key event."""
        self.user_input[KEY_STROKES[event_key]] = event_value

    def add_ammo(self, added_ammo) -> None:
        """Add <added_ammo> to self's ammo attribute, capping it at 999."""
        self.ammo = min(self.ammo + added_ammo, 999)

    def add_score(self, added_score) -> None:
        """Add <added_score> to <self>'s score, doubling if DoubleScore is active."""
        if str(self.power_up) == "DoubleScore":
            self.score += 2 * added_score
        else:
            self.score += added_score

    def add_kills(self, added_kills) -> None:
        """Increase <self>'s kills by <added_kills>."""
        self.kills += added_kills

    def set_shooting(self, is_shooting) -> None:
        """Set <self>'s shooting state to <is_shooting>."""
        self.shooting = is_shooting

# Enemy Class
class Enemy(Character):
    """An enemy character.

    Attributes:
            - direction (str): The direction of the enemy's current movement.
            - directional_timing (int): The amount of time the enemy will
            continue to move in its current direction.
    """
    direction: str
    directional_timing: int
    def __init__(self, location) -> None:
        """Initialize enemy at <location>."""
        super().__init__(location[0], location[1], "assets/character_icons/alien.png")
        self.direction = DIRECTIONS[randint(0, 7)]
        self.directional_timing = randint(60, 300)

    def update(self) -> None:
        """Move enemy and adjust direction on timing or boundary hit."""
        boundary = self.move(MOVEMENT_COEFFICIENTS[self.direction], ENEMY_SPEED)
        self.directional_timing -= 1
        if self.directional_timing == 0:
            self.directional_timing = randint(1, 10) * 30
            self.direction = DIRECTIONS[randint(0, 7)]
        if boundary != "":
            self.direction = choice(OPPOSITE_DIRECTIONS[boundary])

    def check_for_death(self, player) -> bool:
        """Return true if <player>'s area collides with <self>'s area."""
        return self.rect.collidepoint(player.rect.center)


class Bullet:
    """A bullet fired by a UserPlayer.

    Attributes:
        - x (float): The x-coordinate of the character.
        - y (float): The y-coordinate of the character.
        - rect (pygame.Rect): The rectangular area that defines the position
          and size of the character.
        - direction (str): The direction of player's current movement.
    """
    x: float
    y: float
    rect: pygame.Rect
    direction: str
    def __init__(self, x: float, y: float, direction: str) -> None:
        """Initialize a Bullet at <x>, <y> moving in <direction>."""
        self.x = x
        self.y = y
        self.rect = pygame.Rect(int(x - 2), int(y - 2), 4, 4)
        self.direction = direction

    def place(self, screen: pygame.Surface) -> None:
        """Update <self>'s position and draw on <screen>."""
        self.update()
        self.draw(screen)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw <self> on <screen>."""
        pygame.draw.circle(screen, "white", (self.x, self.y), 3)

    def update(self) -> None:
        """Move <self> in its current direction and speed."""
        self.x += MOVEMENT_COEFFICIENTS[self.direction][0] * BULLET_SPEED
        self.y += MOVEMENT_COEFFICIENTS[self.direction][1] * BULLET_SPEED

    def check_for_enemies(self, enemies: list[Enemy]) -> int:
        """Return the number of enemies hit by <self> and remove them from
        <enemies>.
        """
        kills = 0
        for enemy in enemies.copy():
            if enemy.rect.collidepoint((self.x, self.y)):
                enemies.remove(enemy)
                kills += 1
        return kills
